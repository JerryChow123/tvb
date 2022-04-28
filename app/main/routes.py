import os
from datetime import datetime, timezone

import sqlalchemy.engine.row
import station as station
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from sqlalchemy import extract
from werkzeug.utils import secure_filename

import app
from app import current_app, db
from app.main.forms import EditProfileForm, PostForm, ForumReplyForm, ForumPostForm
from app.models import *
from app.main import bp

import app.globalvar


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/')
@bp.route('/index')
def index():
    app.globalvar.init_data()

    # 節目討論區
    stations = Station.query.limit(5).all()
    spoilers_bar = SpoilersBar.query.limit(3).all()
    programme_forum = Programme.query.limit(4).all()

    # 節目表
    now_time = datetime.now()
    nowtime = [
        now_time.strftime("%d/%m/%y"),
        now_time.strftime("%H:%M")
    ]
    programmes = []
    for s in stations:
        record = ProgrammeList.query.with_entities(ProgrammeList.name, ProgrammeList.time).\
            filter(extract('hour', ProgrammeList.time)==now_time.hour,
                   ProgrammeList.station==s.id).\
            order_by(ProgrammeList.time.asc()).all()
        if record != None:
            name = ""
            for i in record:
                if now_time.minute >= i[1].minute:
                    name = i[0]
            if name == "":
                last = ProgrammeList.query.filter(extract('hour', ProgrammeList.time) < now_time.hour,
                                                  ProgrammeList.station==s.id). \
                    order_by(ProgrammeList.time.desc()).first()
                if last != None:
                    name = last.name
            programmes.append(name)
        else:
            programmes.append("")

    latest_recommend = LatestRecommend.query.\
        order_by(LatestRecommend.id.asc()).all()
    j2_recommend = J2Recommend.query.\
        order_by(J2Recommend.id.asc()).all()
    programme_recommend = ProgrammeRecommend.query.\
        order_by(ProgrammeRecommend.id.asc()).all()
    latest_news = LatestNews.query. \
        order_by(LatestNews.date.desc()).limit(8).all()
    entertainment_news = EntertainmentNews.query. \
        order_by(EntertainmentNews.date.desc()).limit(8).all()
    mytv_super = myTVSUPER.query. \
        order_by(myTVSUPER.id.asc()).all()
    bigbig_shop = bigbigshop.query. \
        order_by(bigbigshop.id.asc()).all()
    digital_content = DigitalContent.query. \
        order_by(DigitalContent.id.asc()).all()

    latest_news_utc = []
    for news in latest_news:
        time = news.date.timestamp()
        utc_time = datetime.fromtimestamp(time, tz=timezone.utc)
        latest_news_utc.append(utc_time)

    entertainment_news_utc = []
    for news in entertainment_news:
        time = news.date.timestamp()
        utc_time = datetime.fromtimestamp(time, tz=timezone.utc)
        entertainment_news_utc.append(utc_time)

    return render_template('index.html', title=_('Home'),
                           # 頂部
                           spoilers_bar=spoilers_bar,
                           # 節目表
                           stations=stations,
                           nowtime=nowtime,
                           programmes=programmes,
                           # 最新推介
                           latest_recommend=latest_recommend,
                           # J2 節目推介
                           j2_recommend=j2_recommend,
                           # 節目推介
                           programme_recommend=programme_recommend,
                           # 即時新聞
                           latest_news=latest_news,
                           latest_news_utc=latest_news_utc,
                           # 娛樂新聞
                           entertainment_news=entertainment_news,
                           entertainment_news_utc=entertainment_news_utc,
                           # myTV SUPER
                           mytv_super=mytv_super,
                           # big big shop
                           bigbig_shop=bigbig_shop,
                           # Digital Content
                           digital_content=digital_content,
                           # 節目討論區
                           programme_forum=programme_forum)


@bp.route('/programme')
def programme():
    app.globalvar.init_data()

    stations = Station.query.all()
    programme_time = app.globalvar.programme_time
    # [station] -> [name, time]
    programme_list = []
    for i in range(len(programme_time)):
        row = []
        for s in stations:
            record = ProgrammeList.query.with_entities(ProgrammeList.name, ProgrammeList.time)\
                .filter(extract('hour', ProgrammeList.time)==i,\
                        ProgrammeList.station==s.id)\
                .order_by(ProgrammeList.time.asc()).all()
            row.append(record)
        programme_list.append(row)

    return render_template('programme.html', title=_('Programme'),
                           stations=stations,
                           programme_time=programme_time,
                           programme_list=programme_list)


@bp.route('/forum/<sid>')
def forum(sid):
    page = request.args.get('page', 1, type=int)
    stations = Station.query.all()
    if sid == 'index':
        stations_p = Station.query.paginate(page, 5, False)
        next_url = url_for('main.forum', sid=sid, page=stations_p.next_num) \
            if stations_p.has_next else None
        prev_url = url_for('main.forum', sid=sid, page=stations_p.prev_num) \
            if stations_p.has_prev else None
        return render_template('forum.html', title=_('Programme Forum'),
                               stations=stations_p.items,
                               next_url=next_url,
                               prev_url=prev_url)

    station = Station.query.filter_by(id=sid).first_or_404()
    pid = request.args.get('pid')

    if pid:
        forum_posts = ForumPost.query.filter_by(programme=pid).\
            order_by(ForumPost.date.desc()).paginate(page, 8, False)
        next_url = url_for('main.forum', sid=sid, pid=pid, page=forum_posts.next_num) \
            if forum_posts.has_next else None
        prev_url = url_for('main.forum', sid=sid, pid=pid, page=forum_posts.prev_num) \
            if forum_posts.has_prev else None

        programme = Programme.query.filter_by(id=pid).first()
        user = False
        if current_user.is_authenticated:
            user = True

        return render_template('forum_programme.html', title=_('Programme Forum'),
                               station=station,
                               programme=programme,
                               forum_posts=forum_posts.items,
                               user=user,
                               next_url=next_url,
                               prev_url=prev_url)

    programmes = Programme.query.filter_by(station=sid).\
        paginate(page, 3, False)
    next_url = url_for('main.forum', sid=sid, page=programmes.next_num) \
        if programmes.has_next else None
    prev_url = url_for('main.forum', sid=sid, page=programmes.prev_num) \
        if programmes.has_prev else None
    posts_num = []

    for i in programmes.items:
        posts_num.append(ForumPost.query.filter_by(programme=i.id).count())

    return render_template('station.html', title=_('Programme Forum'),
                           stations=stations,
                           station=station,
                           programmes=programmes.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           posts_num=posts_num)


@bp.route('/forumpost/<pstid>', methods=['GET', 'POST'])
def forumpost(pstid):
    page = request.args.get('page', 1, type=int)
    post = ForumPost.query.filter_by(id=pstid).first_or_404()
    replys = ForumReply.query.filter_by(post=pstid).\
        order_by(ForumReply.date.asc()).paginate(
        page, 5, False)
    next_url = url_for('main.forumpost', pstid=pstid, page=replys.next_num) \
        if replys.has_next else None
    prev_url = url_for('main.forumpost', pstid=pstid, page=replys.prev_num) \
        if replys.has_prev else None

    form = None
    if current_user.is_authenticated:
        form = ForumReplyForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=current_user.username).first()
            db.session.add(
                ForumReply(post=pstid, author=user.id, body=form.body.data, date=datetime.utcnow())
            )
            db.session.commit()
            return redirect(url_for('main.forumpost', pstid=pstid, page=replys.pages))

    return render_template('forum_post.html', title=_('Programme Forum'),
                           station=post.programme_ref.station_ref,
                           programme=post.programme_ref,
                           post=post,
                           replys=replys.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           form=form)



@bp.route('/create_post/<pid>', methods=['GET', 'POST'])
@login_required
def create_post(pid):
    programme = Programme.query.filter_by(id=pid).first()

    form = ForumPostForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        post = ForumPost(author=user.id, programme=programme.id,
                         title=form.title.data, body=form.body.data,
                         date=datetime.utcnow())
        db.session.add(post)

        try:
            db.session.commit()
        except:
            db.session.remove()
            flash(_('Topic is already exists'), 'error')
            return redirect(url_for('main.create_post', pid=pid))

        return redirect(url_for('main.forumpost', pstid=post.id))

    return render_template('forum_programme.html', title=_('Programme Forum'),
                           form=form,
                           station=programme.station_ref,
                           programme=programme)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    if current_user.username == username:
        form = PostForm()
        if form.validate_on_submit():
            post = Post(body=form.post.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash(_('Your post is now live!'))
            return redirect(url_for('main.user', username=user.username))

        return render_template('user.html', title=_('Profile'), user=user, form=form, posts=posts.items,
                               next_url=next_url, prev_url=prev_url)

    return render_template('user.html', title=_('Profile'), user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        if current_user.username != form.username.data and User.query.filter_by(username=form.username.data).first():
            flash(_('User name is already exists'), 'error')
            return redirect(url_for('main.edit_profile'))

        if form.icon.data:
            file = request.files[form.icon.name]
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                exts = filename.split('.')
                filename = current_user.username + '.' + exts[-1]
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                current_user.icon_path = current_app.config['UPLOAD_FOLD'] + filename
            else:
                flash(_('Incorrect Icon File'), 'error')
                return redirect(url_for('main.edit_profile'))

        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username), 'error')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'), 'error')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))
