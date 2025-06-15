from FlaskBlogApp import app
import threading
from FlaskBlogApp.routes import run_tcp_server,clean_records,polling_shadow
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, request, redirect, url_for, make_response
from flask_babel import Babel, _
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'el', 'es', 'fr']

def get_locale():
    lang = request.cookies.get('language')
    print(f"Language from cookie: {lang}")
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        print(f"Returning language: {lang}")
        return lang
    default_lang = request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])
    print(f"Returning default language: {default_lang}")
    return default_lang

babel = Babel(app, locale_selector=get_locale)

@app.route('/change_language/<language>')
def change_language(language=None):
    if language and language in app.config['BABEL_SUPPORTED_LOCALES']:
        referrer = request.referrer if request.referrer else url_for('index')
        response = make_response(redirect(referrer))
        response.set_cookie('language', language)
        return response
    return redirect(url_for('index'))


if __name__ == "__main__":      

   server_thread = threading.Thread(target=run_tcp_server)
   server_thread.start()
   scheduler = BackgroundScheduler()
   scheduler.add_job(clean_records, 'interval', minutes=1)  # Trigger every 1 minute
   ##### REM this if Now Shadow Conntroller Connected
   scheduler.add_job(polling_shadow, 'interval', minutes=1)  # Trigger every 1 minute   
   #######
   scheduler.start()
   #app.run(host="0.0.0.0",debug=False)
   app.run(host='0.0.0.0', port=5000, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
   

   


