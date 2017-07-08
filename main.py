import os 
import hashlib
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from flask import session as secion
from sqlalchemy import create_engine, or_, desc, asc
from sqlalchemy.orm import sessionmaker
from flask_debugtoolbar import DebugToolbarExtension
from db_art import Base, Fotos, User, LikesDislikes, Comentarios, likesID
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.secret_key = 'super_super_secret'
app.debug = True

# SqlAlchemy Settings
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

engine = create_engine('sqlite:///db_art.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Flask Debug Toolbar
# toolbar = DebugToolbarExtension(app)
# set up admind panel
admin = Admin()
admin.init_app(app)
admin.add_view(ModelView(User, session))
admin.add_view(ModelView(Fotos, session))
admin.add_view(ModelView(Comentarios, session))
admin.add_view(ModelView(LikesDislikes, session))
# admin.add_view(ModelView(likesID, Base))
# crear un objeto json para  enviar los errores al
# 
# secion del log in and out
from functools import wraps

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in secion:
            return test(*args,**kwargs)
        else:
            flash('log in para accesar a la pagina')
            return redirect(url_for('form'))
    return wrap


# log in y sign up se confirma por el boton el value login o sign up 
@app.route('/')
@app.route('/Welcome', methods=['GET', 'POST'])
def form(error='',error2='',error3='',errorE='',errorU='',email='',name=''):
    return render_template('login_signup.html',error=error,error2=error2,errorE=errorE,email=email,name=name)

@app.route("/log_in", methods=['POST'])
def log_in():
    if request.method == 'POST':
        email=request.form['email']
        password = request.form['password']
        if request.form['email'] and request.form['password']:
            if session.query(User).filter_by(email= request.form['email']).first():
                user=session.query(User).filter_by(email= request.form['email']).first()
                if user.password == hashlib.sha256(password[1]).hexdigest():
                    secion['logged_in']=True
                    secion['user_id']= user.id
                    flash('cabas de iniciar secion')
                    return redirect(url_for('home',user_id= user.name))
                else:
                    return render_template('login_signup.html',error2='password no es valido',email=email)
            else:
                return render_template('login_signup.html',error='email no encontrado',error2='password no es valido',email=email)
        else:
            return render_template('login_signup.html',error='email no encontrado',error2='password no es valido',email=email)

@app.route("/sign_up", methods=['POST'])
def sign_up():
    username=request.form['uname']
    email=request.form['newemail']
    password1=request.form['password1']
    password2=request.form['password2']
    user_ = session.query(User).filter_by(name = username).first()
    email_= session.query(User).filter_by(email= email).first()
    if not username and not email and not (password1 or password2):
        return render_template('login_signup.html',error3='llenar la casilla',errorU='llenar la casilla',errorE='llenar la casilla',email=email,name=username)
    elif email_ :
        return render_template('login_signup.html',error3='Email existe',email=email,name=username)
    elif user_ :
        return render_template('login_signup.html',errorU=username+' existe',email=email,name=username)
    elif password1 != password2:
        return render_template('login_signup.html',errorE='las passwords no son el mismo',email=email,name=username)
    elif username and email and (password1 == password2) and (user_ is None and email_ is None):
        user = User(name = username,password=hashlib.sha256(password1[1]).hexdigest(),email=email)
        session.add(user)
        session.commit()
        secion['logged_in']=True
        secion['user_id']= user.id
        flash('cabas de iniciar secion')
        return redirect(url_for('home',user_id=user.name))

@app.route("/logout")
@login_required
def logout():
    secion.pop("logged_in")
    secion.pop('user_id')
    flash('secion terminada')
    return redirect(url_for('form'))

@app.route('/Home/<user_id>/', methods=['GET'])
@login_required
def home(user_id):
    user = session.query(User).filter_by(name=user_id).one()
    post = session.query(Fotos).order_by(desc(Fotos.creacion)).all()
    return render_template('galery.html',user=user,images=post)

@app.route('/gallery/<user_id>', methods=['GET'])
@login_required
def gallery(user_id):
    user = session.query(User).filter_by(id=secion['user_id']).one()
    user_gallery= session.query(Fotos).filter_by(user_img_name=user_id).all()
    print user_gallery
    return render_template('galery.html',user=user,images=user_gallery)

@app.route('/gallery/<user_name>/<int:img_id>', methods=['GET'])
@login_required
def img(user_name,img_id):
    user =session.query(User).filter_by(id=secion['user_id']).one()
    user_id = session.query(User).filter_by(name=user_name).one()
    foto = session.query(Fotos).filter_by(id=img_id).one()
    coments =session.query(Comentarios).filter_by(post_id=img_id).all()
    likes= session.query(LikesDislikes).filter_by(post_id=img_id).first()
    if likes is None:
        like = LikesDislikes(post_id=img_id,like=0,dislike=0)
        session.add(like)
        session.commit()
        return render_template('image.html',user=user,img=foto,coments=coments,like=like,user_id=user_id.id)
    return render_template('image.html',user=user,img=foto,coments=coments,like=likes,user_id=user_id.id)

@app.route('/new_img/<user_id>', methods=['GET','POST'])
@login_required
def new_post(user_id):
    return render_template('upload.html',user=session.query(User).filter_by(id=secion['user_id']).one())

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    # folder_name = user_id
    '''
    # this is to verify that folder to upload to exists.
    if os.path.isdir(os.path.join(APP_ROOT, 'files/{}'.format(folder_name))):
        print("folder exist")
    '''
    # target = os.path.join(APP_ROOT, 'static/img/')#.format(folder_name)
    target = 'static/img/'
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        # This is to verify files are supported
        ext = os.path.splitext(filename)[1]
        if (ext == ".jpg") or (ext == ".png"):
            print("File supported moving on...")
        else:
            render_template("Error.html", message="Files uploaded are not supported...")
        destination = "".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)
        user = session.query(User).filter_by(id=secion['user_id']).one()
        foto =Fotos(name=request.form['name'],tag=request.form['tags'],folder='img/'+filename,estilo=request.form['estilo'],user_id=user.id,user_img_name=user.name)
        session.add(foto)
        session.commit()
        print foto.creacion.strftime('%y/%m/%d')
    # return send_from_directory("images", filename, as_attachment=True)
    return redirect(url_for('img',user_name=user.name,img_id=foto.id))
    
@app.route('/like/', methods=["POST"])
@login_required
def likes():
    img_id = request.form["img_id"]
    print 'hello'
    like = session.query(LikesDislikes).filter_by(post_id=img_id).one()
    like.like+=1
    session.add(like)
    session.commit()
    return jsonify('new like guardado')

@app.route('/dislike/',methods=['POST'])
@login_required
def dislikes():
    img_id = request.form['img_id']
    print img_id
    like = session.query(LikesDislikes).filter_by(post_id=img_id).one()
    like.dislike+=1
    session.add(like)
    session.commit()
    return jsonify('new like guardado')


@app.route('/comments/<user_id>/<int:img_id>',methods=['POST'])
@login_required
def comments(user_id,img_id):
    user = session.query(User).filter_by(id=secion['user_id']).one()
    if user_id == user.name:
        coment = Comentarios(content=request.form['comments'],user_id=user.id,post_id=img_id)
        session.add(coment)
        session.commit()
    return redirect(url_for('img',user_name=user_id,img_id=img_id))

@app.route('/delete/<int:user_id>/<int:foto_id>', methods=['GET'])
@login_required
def delete(user_id,foto_id):
    user = session.query(User).filter_by(id=secion['user_id']).one()
    if user_id == user.id:
        foto= session.query(Fotos).filter_by(id=foto_id,user_id=user_id).one()
        session.delete(foto)
        session.commit()
        return redirect(url_for('gallery',user_id=user.name))

@app.route('/edit<int:user_id>/<int:img_id>', methods=['GET'])
@login_required
def informacion(user_id,img_id):
    user = session.query(User).filter_by(id=secion['user_id']).one()
    foto = session.query(Fotos).filter_by(id=img_id).one()
    print foto.tag
    if user_id == user.id:
        return render_template('complete.html',user=user,img=foto)

@app.route("/editar/<int:user_id>/<int:img_id>", methods=['POST'])
@login_required
def editar(user_id, img_id):
    user = session.query(User).filter_by(id=secion['user_id']).one()
    img = session.query(Fotos).filter_by(id=img_id).one()
    img.name=request.form['name']
    img.tag=request.form['tags']
    img.estilo=request.form['estilo']
    session.add(img)
    session.commit()
    return redirect(url_for('img',user_name=user.name,img_id=img.id))

@app.route('/estilos/<estilo>', methods=["GET","POST"])
@login_required
def estilos(estilo):
    user = session.query(User).filter_by(id=secion['user_id']).one()
    user_gallery = session.query(Fotos).filter_by(estilo=estilo).all()
    return render_template('galery.html',user=user,images=user_gallery)

@app.route('/estilos', methods=["GET","POST"])
@login_required
def lista():
    user=session.query(User).filter_by(id=secion['user_id']).one()
    return render_template('coment.html',user=user)

@app.route('/likes/<user_name>')
@login_required
def likesuser(user_name):
    user = session.query(User).filter_by(id=secion['user_id']).one()
    fotos= session.query(Fotos,likesID).filter_by(user_id=secion['user_id']).all()
    return render_template('galery.html',user=user,images=fotos)

@app.route('/test')
@login_required
def test():
    return render_template('likestest.html')


if __name__ == '__main__':
app.run(host='0.0.0.0', port=5000)