from app import app
import os
from werkzeug.utils import secure_filename
from flask import Response, redirect, render_template, request, send_file, flash, url_for,session
#import logging
import pyminizip as pz
import glob
import secrets
import string
from datetime import datetime
from tempfile import TemporaryDirectory, TemporaryFile,mkdtemp
import io
import shutil
import pyzipper

app.secret_key = "hello" # for encrypting the session

UPLOAD_FOLDER =  os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

path_temp_dir = "D:"
app.config['PATH_TEMP_DIR'] = path_temp_dir
 

def password_gen():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        #logging.info('Into Get Index')
        if 'temp_dir' in session:
            temp_dir_part = session['temp_dir']
            #logging.info("index: check is have session temp_dir "+temp_dir_part)
            if os.path.isdir(temp_dir_part):
                shutil.rmtree(temp_dir_part)
                #logging.info("index: Remove temp_dir ")

        temp_dir = mkdtemp(prefix='python_zf_',dir=app.config['PATH_TEMP_DIR'])
        session['temp_dir'] = temp_dir
        #logging.info("inpex: temp_dir part: "+temp_dir)
        out = os.path.isdir(temp_dir)
        #logging.info("index: check have temp_dir is "+str(out))
        auto_password = password_gen()
        datetime_string = datetime.now().strftime("%d%m%Y%H%M%S")
        return render_template("index.html", autogen = auto_password,datetime_str = datetime_string)

    flash('Error','danger')
    return render_template("404.html")


@app.route('/upload', methods=['GET','POST'])
def uploader():
    try: 
        if request.method == 'POST':
            #logging.info("into upload post")
            temp_dir_path = session['temp_dir']
            out = os.path.isdir(temp_dir_path)
            #logging.info("upload: check have temp_dir is "+str(out))
            if not (os.path.isdir(temp_dir_path)):
                flash("Zip File has been exported or files in temporary directory deleted, Please select files again.  ",'danger')
                #logging.error("upload: Zip File has been exported or files in temporary directory deleted, Please select files again. ")
                return redirect(url_for('index'))
            #logging.info("upload: path temp_dir: "+temp_dir_path)

            if 'files[]' not in request.files:
                if os.path.isdir(temp_dir_path):
                    shutil.rmtree(temp_dir_path)
                flash('No file part files[]','danger')
                #logging.error('upload: No files[] ')
                return  redirect(url_for('index'))

            files_list = []
            if request.files:
                if 'files[]' not in request.files:
                    if os.path.isdir(temp_dir_path):
                        shutil.rmtree(temp_dir_path)
                    #logging.error("upload: No file part")
                    flash('upload: No file part','danger')
                    return redirect(url_for('index'))
                files_list = request.files.getlist('files[]')
            
            for f in files_list: 
                    if f.filename == "":
                        if os.path.isdir(temp_dir_path):
                            shutil.rmtree(temp_dir_path)
                        #logging.error("upload: Name file is null")
                        flash("Name file is null",'danger')
                        return redirect(url_for('index'))
                    #logging.info("upload: name file: "+f.filename)
                    #filename = secure_filename(f.filename)#Not use secure filename - 'boo r.txt'--> 'boo_r.txt'
                    #logging.info(os.path.join(temp_dir_path,f.filename))
                    f.save(os.path.join(temp_dir_path,f.filename))
                    #logging.info('save file success')

            #logging.info("upload: saved files in uploads success")  
            flash("saved files in uploads success" ,'danger')
            return render_template("index.html",upload_finish = "yes")
        
        
        flash("Not post method" ,'danger')
        #logging.error("upload: Not post method")
        return  redirect(url_for('index'))
    except :
        #logging.error("upload: error upload method")
        if os.path.isdir(session['temp_dir']):
            shutil.rmtree(session['temp_dir'])
        #logging.error("upload: temp_dir cleanup")
        flash("error upload method" ,'danger')
        return redirect(url_for('index'))



@app.route('/export', methods=['GET','POST'])
def exporter():
    try:
        if request.method == "POST":
            temp_dir_path = session['temp_dir']
            datetime_string = request.form["datetime_str"] 

            password = None
            type_pass = request.form["typPass"]
            if(type_pass == "autogen"):
                password = request.form["autogen"]
            if(type_pass == "manual"):
                password = request.form["manual"]            
            if(type_pass == "nouse"):
                password = None

            if request.form["submit"] == "savepassword_autogen" :
                #logging.info("export: into auto save password")
                return redirect(url_for('savepassword',datetime_str=datetime_string,password_str=password))

            if request.form["submit"] == "savepassword_manual" :
                #logging.info("export: into manual save password")
                return redirect(url_for('savepassword',datetime_str=datetime_string,password_str=password))

            if request.form["submit"] == "refresh" :
                #logging.info("export: into refresh")
                if os.path.isdir(temp_dir_path):
                    shutil.rmtree(temp_dir_path)
                #logging.info("export: temp_dir cleanup")
                flash('Refresh form success.','success')
                return redirect(url_for('index'))

            if not (os.path.isdir(temp_dir_path)):
                flash("Zip File has been exported or files in temporary directory deleted, Please select files again.  ",'danger')
                #logging.error("export: Zip File has been exported or files in temporary directory deleted, Please select files again. ")
                return redirect(url_for('index'))

            selected_filename = request.form.getlist("selected_filename") 
            #logging.info("export: Selected filename"+ ', '.join([str(elem) for elem in selected_filename]))
            if not selected_filename:
                if os.path.isdir(temp_dir_path):
                    shutil.rmtree(temp_dir_path)
                #logging.info("export: temp_dir cleanup")
                flash("No file(s) selected in 'Files list to archive' section. ",'danger')
                #logging.error("export: No file(s) selected in 'Selected files' section. ")
                return redirect(url_for('index'))

            if len(selected_filename) == 1:
                if os.path.isdir(temp_dir_path):
                    shutil.rmtree(temp_dir_path)
                #logging.info("export: temp_dir cleanup")
                flash("No file(s) selected in 'Files list to archive' section. ",'danger')
                #logging.error("export: No file(s) selected in 'Selected files' section. ")
                return redirect(url_for('index'))


            file_name = []
            file_path = []
            #file_non = []
            zipname = datetime_string+"compress_file.zip"
            response = Response(content_type='application/zip')
            temp_path_zipfile = os.path.join(temp_dir_path,zipname)
            for root, dirs, files in os.walk(temp_dir_path):
                    for fname in files:
                        if fname in selected_filename:
                            file_path.append(os.path.join(root,fname))
                            #file_non.append('')
                            file_name.append(fname)
            #logging.info('export: file in tempdir:'+', '.join([str(elem) for elem in files]))
            if not file_path :
                flash("No file(s) matching in temporary directory, Please select files again.",'danger')
                #logging.error("export: No file(s) matching in temp_dir (file_path list is null)")
                return redirect(url_for('index'))

            #pz.compress_multiple(file_path, file_non,temp_path_zipfile, password, 5)
            with pyzipper.AESZipFile(temp_path_zipfile,'w',compresslevel=5) as zf:
                if(password):
                    zf.setencryption(pyzipper.WZ_AES)
                    zf.setpassword(password.encode())
                for fn in file_name:
                    zf.write(os.path.join(temp_dir_path,fn),arcname=fn)
            #logging.info("export: create zipfile success")

            with open(temp_path_zipfile, "rb") as f:
                    content = io.BytesIO(f.read())
                    response = send_file(content,
                                as_attachment=True,
                                attachment_filename="%scompress_file.zip" % datetime_string)
                    #logging.info("export: response zipfile success")
           
            shutil.rmtree(temp_dir_path)
            #session.pop("temp_dir",None)
            #logging.info("export: temp_dir cleanup")
            return response
    
        flash("error not response zipfile" ,'danger')
        #logging.error("export: error not response zipfile" ,'danger')
        return redirect(url_for('index'))

    except :
        if os.path.isdir(temp_dir_path):
            shutil.rmtree(session["temp_dir"])
        #logging.error("error in exception export method")
        flash("An error occurred in the compression method. Because there are too many files, or the file size is too large. or the filename is not secure." ,'danger')
        flash("Reduce the number of files to compress at a time or rename the files using English excluding spaces and symbols","warning")
        return redirect(url_for('index'))


@app.route('/savepassword', defaults={'datetime_str': None,'password_str': None})
@app.route('/savepassword/<datetime_str>/<password_str>')
def savepassword(datetime_str,password_str):
    try:
        response = Response(content_type='application/text')
        with TemporaryFile() as fp:
            fp.write(password_str.encode('utf-8')) 
            fp.seek(0)
            content = io.BytesIO(fp.read())
            response = send_file(content,
                                as_attachment=True,
                                attachment_filename="%scompress_file_password.txt" % datetime_str)
            return response

    except :
        #logging.error('error savepassword method')
        flash('error savepassword method' ,'danger')
        return redirect(url_for('index'))


@app.route('/closeapp',methods=['GET','POST'])
def closeapp():
    if request.method == 'POST':
        #logging.info("Into closeapp")
        if 'temp_dir' in session:
            temp_dir_part = session['temp_dir']
            #logging.info("closeapp: check is have session temp_dir "+temp_dir_part)
            if os.path.isdir(temp_dir_part):
                shutil.rmtree(temp_dir_part)
                #logging.info("closeapp: Remove temp_dir ")

            #session.clear()
        #logging.info('closeapp: clear temp_dir')

    return "<div> 'closing tab' </div>"