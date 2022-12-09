from flask import Flask, render_template, request,send_file, flash
from yahoobeautifulsoup import main
import config
from starttasks import make_celery
from celery.result import AsyncResult
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = config.OAUTHLIB_RELAX_TOKEN_SCOPE

app = Flask(__name__)
app.config.update(
    # TESTING=True,
    SECRET_KEY=config.SECRET,
    CELERY_CONFIG={
        'broker_url': config.BROKER,
        'result_backend': config.RESULT_BACKEND
    }
)

celery = make_celery(app)
@celery.task()
def trigger_scraping_job(file_name):

    returned_file_name = main.async_scraper(file_name)
    return returned_file_name


@app.route('/', methods=['GET', 'POST'])
def scrape_yahoo():

    if request.method == 'POST':
        file_name = request.form.get('file_name')
        if os.path.exists(f"{file_name}.xlsx"):
            os.remove(f"{file_name}.xlsx")
        if file_name:
            task = trigger_scraping_job.delay(file_name=file_name)
            return render_template('index.html', form_submitted=True, task_id=task.id, file_name=file_name)
    return render_template('index.html')


@app.route('/xlsx_download', methods=['GET', 'POST'])
def xlsx_download():
    task_id = request.args.get("task_id")
    filename = request.args.get("filename")

    res = AsyncResult(task_id, app=celery)
    if res.ready() and os.path.exists(f"{filename}.xlsx"):
        return send_file(f"{filename}.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True)
    else:
        print('flashing')
        flash('File is not ready yet or the job is unsuccessful, try again some seconds later.')

    return render_template('index.html', form_submitted=True, task_id=task_id, file_name=filename)