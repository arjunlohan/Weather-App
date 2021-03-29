import sys
from flask import request, redirect, Flask, render_template, flash
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from os import environ

# write your code here
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SECRET_KEY'] = environ.get('SESSION_KEY') or 'pass'
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(80), unique=False, nullable=False)
    city_weather_state = db.Column(db.String(80), unique=False, nullable=False)
    city_weather_temp = db.Column(db.String(4), unique=False, nullable=False)
    city_time_image = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '{}'.format(self.city_name)


db.create_all()


def day_or_night(currenttime, sunrisetime, sunsettime):
    if int(currenttime) < int(sunrisetime):
        return "evening-morning"
    elif int(currenttime) < int(sunsettime):
        return "day"
    else:
        return "night"


@app.route('/')
def index():
    return render_template('index.html', data=City.query.all())


@app.route('/add', methods=['GET', 'POST'])
def add_city():
    get_user_city_name = ''.join(request.form.getlist('city_name'))
    if str(get_user_city_name) == str(City.query.filter_by(city_name=get_user_city_name).first()):
        print("The city has already been added to the list!")
        flash("The city has already been added to the list!")
        return redirect('/')
    else:
        api_key = 'f4f61fa3eeb5ccac21d8d8be41928bcb'
        dict_with_weather_info = requests.get(
            'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(get_user_city_name, api_key))
        if int(dict_with_weather_info.status_code) >= 400:
            flash("The city doesn't exist!")
        else:
            #print(json.loads(dict_with_weather_info.content))
            city_info_test = City(city_name=str(json.loads(dict_with_weather_info.content)["name"]),
                                  city_weather_state=str({k:v for e in json.loads(dict_with_weather_info.content)["weather"] for (k,v) in e.items()}.get("main")),
                                  city_weather_temp=str(int(json.loads(dict_with_weather_info.content)["main"].get("temp")-273.15)),
                                  city_time_image=str(day_or_night(json.loads(dict_with_weather_info.content)['dt'],
                                                                   json.loads(dict_with_weather_info.content)['sys'].get('sunrise'),
                                                                   json.loads(dict_with_weather_info.content)['sys'].get('sunset'))))

            db.session.add(city_info_test)
            db.session.commit()
            #CityInfo.query.all() - Check the overall database
        return redirect('/')


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
