
from flask import render_template, request, redirect, session, url_for
from flask import send_from_directory, abort, flash
from flask import Flask

from functools import wraps

from app import app

import pymysql.cursors
import hashlib
import os, sys, stat
from werkzeug.utils import secure_filename

conn = pymysql.connect(host=app.config['DBHOST'],
                       user=app.config['DBUSER'],
                       password=app.config['DBPASS'],
                       db=app.config['DBNAME'],
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

def login_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if not 'username' in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return dec

def authenticated():
    return "username" in session

def get_fname():
    if not authenticated():
        return ""
    if 'first_name' in session:
        return session['first_name']
    uname = session['username']

    q = 'SELECT first_name FROM Person WHERE username = %s'

    with conn.cursor() as cursor:
    	cursor.execute(q, (uname))
    	result = cursor.fetchone()
    
    session['first_name'] = result['first_name']
    return session['first_name']

#Routes Index Page
@app.route('/')
def index():
    return render_template("index.html", title='PriCoSha', isAuthenticated=authenticated(), fname=get_fname())

#Routes About Page
@app.route('/about/')
def about():
    return render_template("about.html", title='About', isAuthenticated=authenticated(), fname=get_fname())

#Routes Login Page
@app.route('/login')
@app.route('/login/')
def login():
    return render_template("login.html", title='Login')

#Routes Register Page
@app.route('/register')
@app.route('/register/')
def register():
    return render_template("register.html", title='Register')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
        
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s and password = %s'
    cursor.execute(query, (username, hashlib.md5(password.encode('utf-8')).hexdigest()))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid username or password.'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    passconf = request.form['pass-conf']
    if password != passconf:
        error = "Passwords do not match."
        return render_template('register.html', error=error)
    fname = request.form['fname']
    lname = request.form['lname']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = username + " is taken. Try another."
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO Person (username, password, first_name, last_name) VALUES(%s, %s, %s, %s)'
        cursor.execute(ins, (username, hashlib.md5(password.encode('utf-8')).hexdigest(), fname, lname))
        conn.commit()
        cursor.close()
        session['username'] = username
        return redirect(url_for('home'))

# def retrieveData():
#     username = session['username']
#     cursor = conn.cursor();
#     query = 'SELECT timest, content_name, file_path FROM Content WHERE username = %s ORDER BY timest DESC'
#     cursor.execute(query, (username))
#     data = cursor.fetchall()
#     query = 'SELECT first_name FROM Person WHERE username = %s'
#     cursor.execute(query, (username))
#     data2 = cursor.fetchone()
#     cursor.close()
#     return {"username": username, "posts": data, "fname": data2['first_name']}

# #Routes Home Page Once Logged In
# @app.route('/homeold')
# @login_required
# def home():
#     data = retrieveData()
#     uname = session['username']
#     return render_template('home.html', username=uname, posts=data["posts"], fname=get_fname())


@app.route('/home')
@login_required
def home():
    uname = session['username']
    cursor = conn.cursor()

    searchQuery = request.args.get('q')

    if not searchQuery:
        q =  'SELECT id, file_path, content_name, timest,\
        		username, first_name, last_name, public\
              FROM Content NATURAL JOIN Person\
              WHERE username = %s\
              OR public\
              OR id in\
              	(SELECT id\
              	 FROM Share JOIN Member ON\
              	 	Share.username = Member.username_creator\
              	 	AND Share.group_name = Member.group_name\
              	 WHERE Member.username = %s)\
              ORDER BY timest DESC'
        cursor.execute(q, (uname, uname))
    else:
        q =  'SELECT id, file_path, content_name, timest,\
            username, first_name, last_name\
          FROM Content NATURAL JOIN Person\
          WHERE (username = %s\
          OR public\
          OR id in\
            (SELECT id\
             FROM Share JOIN Member ON\
                Share.username = Member.username_creator\
                AND Share.group_name = Member.group_name\
             WHERE Member.username = %s)\
            )\
          AND (\
               content_name like %s\
            OR username like %s)\
          ORDER BY timest DESC'
        cursor.execute(q, (uname, uname, searchQuery, searchQuery))

    data = cursor.fetchall()

    q1 = 'SELECT username, first_name, last_name, timest, comment_text\
    	  FROM Comment NATURAL JOIN Person\
    	  WHERE id = %s\
    	  ORDER BY timest DESC'

    q2 = 'SELECT first_name, last_name\
    	  FROM Tag JOIN Person ON\
    	  	Tag.username_taggee = Person.username\
    	  WHERE id = %s AND status = true\
    	  ORDER BY timest DESC'

    for d in data:
    	cursor.execute(q1, (d['id']))
    	d['comments'] = cursor.fetchall()

    	cursor.execute(q2, (d['id']))
    	d['tags'] = cursor.fetchall()

    cursor.close()
    return render_template('home.html', username=uname, posts=data, fname=get_fname())


#Logging out
@app.route('/logout')
def logout():
    session.pop('first_name')
    session.pop('username')
    return redirect('/')

#Posting
@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    uname = session['username']
    cursor = conn.cursor();
    cname = request.form['name']
    photo = request.files['file']
    is_public = 1 if request.form.get('public') == "public" else 0
    if photo:
        filename = secure_filename(photo.filename)
        os.chmod(app.config["PHOTO_DIRECTORY"], 0o775)
        photo.save(os.path.join(app.config["PHOTO_DIRECTORY"], filename))
        q = 'INSERT INTO Content(content_name, file_path, username, public) VALUES(%s, %s, %s, %s)'
        cursor.execute(q, (cname, filename, uname, int(is_public)))
    else:
        q = 'INSERT INTO Content(content_name, username, public) VALUES (%s, %s, %s)'
        cursor.execute(q, (cname, uname, is_public))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

# Retrieve user photos only if logged in
@app.route('/content/<path:filename>')
def retrieve_file(filename):
    if not authenticated():
        abort(404)
    uname = session['username']
    cursor = conn.cursor()
    q = "SELECT file_path FROM Content WHERE username = %s AND file_path = %s"
    cursor.execute(q, (uname, filename))
    res = cursor.fetchone()
    if res:
        return send_from_directory(app.config['PHOTO_DIRECTORY'], filename)
    else:
        abort(404)

@app.route('/comment', methods=['POST'])
@login_required
def comment():
	uname = session['username']
	id = request.form['id']
	comment_text = request.form['comment']

	if comment_text == '':
		return redirect(url_for('home'))

	q = 'INSERT INTO Comment(id, username, comment_text) VALUES (%s, %s, %s)'
	cursor = conn.cursor()
	cursor.execute(q, (id, uname, comment_text))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/commentdel', methods=['GET'])
@login_required
def commentdel():
	uname = session['username']

	#extract params
	id = request.args.get('id')
	commenter = request.args.get('username')
	ts = request.args.get('ts')

	# get content owner
	q = 'SELECT username\
		 FROM Content\
		 WHERE id = %s'
	cursor = conn.cursor()
	cursor.execute(q, (id))
	item_owner = cursor.fetchone()['username']

	if uname != item_owner and uname != commenter:
		return redirect(url_for('home'))

	q = 'DELETE FROM Comment\
		 WHERE id = %s\
		 AND username = %s\
		 AND timest = %s'

	cursor.execute(q, (id, commenter, ts))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

def fetch_friend_data(uname):
    with conn.cursor() as cursor:
        cursor = conn.cursor()
        q = """
            SELECT first_name,
                last_name, id,
                Tag.timest, content_name,
                username_tagger,
                username_taggee
            FROM Person JOIN Tag
                ON Person.username = Tag.username_tagger
                JOIN Content USING(id) 
            WHERE not status
            AND username_taggee = %s
            ORDER BY timest DESC
            """

        cursor.execute(q, (uname))
        tags_pending = cursor.fetchall()

        q = """
            SELECT first_name,
                last_name, id,
                Tag.timest, content_name,
                username_tagger,
                username_taggee
            FROM Person JOIN Tag
                ON Person.username = Tag.username_taggee
                JOIN Content USING(id) 
            WHERE not status
            AND username_tagger = %s
            ORDER BY timest DESC
            """

        cursor.execute(q, (uname))
        tags_proposed = cursor.fetchall()


        q = """
            SELECT group_name, description
            FROM FriendGroup
            WHERE username = %s
            """

        cursor.execute(q, (uname))
        groups = cursor.fetchall()

        q = """
            SELECT first_name, last_name
            FROM Person NATURAL JOIN Member
            WHERE group_name = %s
            AND username_creator = %s
            """

        for g in groups:
            cursor.execute(q, (g['group_name'], uname))
            g['members'] = cursor.fetchall()

    return {
        'tags_pending': tags_pending,
        'tags_proposed': tags_proposed,
        'groups': groups
    }


@app.route('/friends')
@login_required
def friends():
    d = fetch_friend_data(session['username'])
    return render_template(
        'friends.html',
        tags_pending=d['tags_pending'],
        tags_proposed=d['tags_proposed'],
        groups=d['groups'],
        fname=get_fname()
        )

@app.route('/tag', methods=['POST'])
@login_required
def tag():
	uname = session['username']

	taggee = request.form['taggee']
	id = request.form['id']

	cursor = conn.cursor()
	q = """
		INSERT INTO Tag(username_tagger, username_taggee, id, status)
		VALUES (%s, %s, %s, %s)
		"""

	if uname == taggee:
		cursor.execute(q, (uname, uname, id, 1))
		conn.commit()
	else:
		#verify the taggee is valid
		v = """
			SELECT id
			FROM Content
			WHERE id = %s
			AND (
				public
				OR id IN (
					SELECT id
					FROM Share JOIN Member ON
					Share.username = Member.username_creator
					AND Share.group_name = Member.group_name
					Where Member.username = %s
				)
			)
			"""
		cursor.execute(v, (id, taggee))
		res = cursor.fetchone()

		if res:
			cursor.execute(q, (uname, taggee, id, 0))
			conn.commit()
		else:
			e = """
				Not a valid tag. {} cannot view that item.
				""".format(taggee)
			flash(e, "danger")

	cursor.close()
	return redirect(url_for('home'))


@app.route('/tagaccept')
@login_required
def tagaccept():
    uname = session['username']

    tagger = request.args.get('tagger')
    taggee = request.args.get('taggee')
    id = request.args.get('id')

    if uname != taggee:
        return redirect(url_for('friends'))

    cursor = conn.cursor()
    q = """
        UPDATE Tag
        SET status = true
        WHERE id = %s
        AND username_tagger = %s
        AND username_taggee = %s
        """
    cursor.execute(q, (id, tagger, taggee))
    conn.commit()
    cursor.close()
    return redirect(url_for('friends'))

@app.route('/tagdecline')
@login_required
def tagdecline():
    uname = session['username']

    tagger = request.args.get('tagger')
    taggee = request.args.get('taggee')
    id = request.args.get('id')

    if uname != taggee:
        return redirect(url_for('friends'))

    cursor = conn.cursor()
    q = """
        DELETE FROM Tag
        WHERE id = %s
        AND username_tagger = %s
        AND username_taggee = %s
        """
    cursor.execute(q, (id, tagger, taggee))
    conn.commit()
    cursor.close()
    return redirect(url_for('friends'))

@app.route('/groupadd', methods=['POST'])
@login_required
def groupadd():
    uname = session['username']

    group_name = request.form['group_name']
    desc = request.form['description']

    q = """
    	INSERT INTO FriendGroup(group_name, username, description)
    	VALUES (%s, %s, %s)
    	"""

    try:
    	with conn.cursor() as cursor:
    		cursor.execute(q, (group_name, uname, desc))
    	conn.commit()
    except pymysql.err.IntegrityError:
    	m = """
    		You already have a group named {}.
    		""".format(group_name)
    	flash(m, "danger")

    return redirect(url_for('friends'))

@app.route('/memberadd', methods=['POST'])
@login_required
def memberadd():
    uname = session['username']
    group_name = request.form['group_name']
    fname = request.form['fname']
    lname = request.form['lname']
    
    q = """
        SELECT username
        FROM Person
        WHERE first_name = %s
        AND last_name = %s
        """

    cursor = conn.cursor()
    cursor.execute(q, (fname, lname))
    res = cursor.fetchall()
    
    if len(res) == 0:
        m = """
            There is no user {} {}.
            """.format(fname, lname)
        flash(m, "warning")
    elif len(res) > 1:
        #need to implement better solution
        e = "Multiple users have that name. Select the username you wish to add."
        d = fetch_friend_data(session['username'])
        return render_template(
            'friends.html',
            tags_pending=d['tags_pending'],
            tags_proposed=d['tags_proposed'],
            groups=d['groups'],
            duplicate_name_error=True,
            usernames=res,
            fname=get_fname()
            )
    else:
        member = res[0]['username']
        q = """
			INSERT INTO Member(username, group_name, username_creator)
			VALUES (%s, %s, %s)
			"""
        try:
            cursor.execute(q, (member, group_name, uname))
            conn.commit()
            m = "{} successfully add to {}".format(member, group_name)
            flash(m, "success")
        except pymysql.err.IntegrityError as e:
            m = "{} is already in {}.".format(member, group_name)
            flash(m, "warning")
        
    cursor.close()
    return redirect(url_for('friends'))

@app.route('/memberaddu', methods=['POST'])
@login_required
def memberaddu():
    uname = session['username']
    member = request.form['username']
    group_name = request.form['group_name']

    q = """
        INSERT INTO Member(username, group_name, username_creator)
        VALUES (%s, %s, %s)
        """

    with conn.cursor() as cursor:
        try:
            cursor.execute(q, (member, group_name, uname))
            conn.commit()
            m = "{} successfully add to {}".format(member, group_name)
            flash(m, "success")
        except pymysql.err.IntegrityError as e:
            m = "{} is already in {}.".format(member, group_name)
            flash(m, "warning")
        
    return redirect(url_for('friends'))


@app.route('/share', methods=['POST'])
@login_required
def share():
    uname = session['username']
    group = request.form['group_name']
    owner = request.form['owner']
    id = request.form['id']

    if owner == "":
        owner = uname

    q = """
        INSERT INTO Share(id, group_name, username)
        VALUES (%s, %s, %s)
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(q, (id, group, owner))
        conn.commit()
        m = """
            Item successfully shared.
            """
        flash(m, 'success')
    except pymysql.err.IntegrityError:
        m = """
            The item is already shared with that group.
            """
        flash(m, "warning")

    return redirect(url_for('home'))

#Searching
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    username = session['username']
    cursor = conn.cursor()
    searchQuery = request.form['query']

    q =  'SELECT id, file_path, content_name, timest,\
            username, first_name, last_name\
          FROM Content NATURAL JOIN Person\
          WHERE (username = %s\
          OR public\
          OR id in\
            (SELECT id\
             FROM Share JOIN Member ON\
                Share.username = Member.username_creator\
                AND Share.group_name = Member.group_name\
             WHERE Member.username = %s))\
          AND (\
               content_name like "\%%s%"\
            OR username like "\%%s%")\
          ORDER BY timest DESC'

    cursor.execute(q, (searchQuery))
    data = cursor.all()
    cursor.close()
    return render_template("home.html", username=username, posts=data, fname=get_fname())
