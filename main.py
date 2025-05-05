from idlelib.debugobj_r import remote_object_tree_item

from bson import ObjectId
from flask import Flask,request,render_template,redirect,session
from pyexpat.errors import messages
import datetime
app=Flask(__name__)
import pymongo
import os
App=os.path.dirname(os.path.abspath(__file__))
profiles=App+"/static/profiles"
myclient=pymongo.MongoClient("mongodb://localhost:27017")
mydatabase=myclient["airline"]
locations_collection=mydatabase["locations"]
airports_collection=mydatabase["airports"]
airlines_collection=mydatabase["airlines"]
airplanes_collection=mydatabase["airplanes"]
schedules_collection=mydatabase["schedules"]
boarding_pass_collection=mydatabase["boarding_pass"]
bookings_collection=mydatabase["bookings"]
payments_collection=mydatabase["payments"]
customers_collection=mydatabase["customers"]
app.secret_key="sravani"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin_login")
def admin():
    return render_template("admin_login.html")

@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username=request.form.get("username")
    password = request.form.get("password")
    if username=="admin" and password == "admin":
        session["role"]="admin"
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="Invalid Login")

@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")

@app.route("/customer_login")
def customer_login():
    return render_template("customer_login.html")

@app.route("/customer_login_action",methods=['post'])
def customer_login_action():
    email=request.form.get("email")
    password=request.form.get("password")
    query={"email":email,"password":password}
    count=customers_collection.count_documents(query)
    if count>0:
        customer=customers_collection.find_one(query)
        session['customer_id']=str(customer['_id'])
        session['role']="customer"
        return redirect("/customer_home")
    return render_template("message.html",message="invalid details")

@app.route("/customer_registration")
def customer_registration():
    return render_template("customer_registration.html")

@app.route("/customer_registration_action",methods=['post'])
def customer_registration_action():
    first_name=request.form.get("first_name")
    last_name=request.form.get("last_name")
    email=request.form.get("email")
    phone=request.form.get("phone")
    password=request.form.get("password")
    address=request.form.get("address")
    state=request.form.get("state")
    city=request.form.get("city")
    zipcode=request.form.get("zipcode")
    query={"email":email}
    count=customers_collection.count_documents(query)
    if count>0:
        return render_template("message.html",message="Duplicate Email Address")
    query={"phone":phone}
    count=customers_collection.count_documents(query)
    if count>0:
        return render_template("message.html",message="Duplicate Phone Number")
    query={"first_name":first_name,"last_name":last_name,"phone":phone,"email":email,"password":password,"address":address,"state":state,"city":city,"zipcode":zipcode}
    customers_collection.insert_one(query)
    return render_template("message.html",message="Customer Registration Successful")

@app.route("/customer_home")
def customer_home():
    return render_template("customer_home.html")

@app.route("/airline_login")
def airline_login():
    return render_template("airline_login.html")

@app.route("/airline_login_action",methods=['post'])
def airline_login_action():
    email=request.form.get("email")
    password=request.form.get("password")
    query={"email":email,"password":password}
    count=airlines_collection.count_documents(query)
    if count>0:
        airline=airlines_collection.find_one(query)
        session['airline_id']=str(airline['_id'])
        session['role']="airline"
        return redirect("/airline_home")
    return render_template("message.html",message="invalid details")

@app.route("/airline_registration")
def airline_registration():
    query = {}
    airlines = airlines_collection.find(query)
    airlines = list(airlines)
    message=request.args.get("message")
    return render_template("airline_registration.html",airlines=airlines,message=message)

@app.route("/airline_registration_action",methods=['post'])
def airline_registration_action():
    airline=request.form.get("airline")
    email=request.form.get("email")
    phone=request.form.get("phone")
    password=request.form.get("password")
    established_year=request.form.get("established_year")
    address=request.form.get("address")
    about=request.form.get("about")
    query = {"email": email}
    count = airlines_collection.count_documents(query)
    if count > 0:
        return redirect("/airline_registration?message=Duplicate Email Number")
    query = {"phone": phone}
    count = airlines_collection.count_documents(query)
    if count > 0:
        return redirect("/airline_registration?message=Duplicate Phone Number")
    query={"airline":airline,"email":email,"phone":phone,"password":password,"established_year":established_year,"address":address,"about":about}
    airlines_collection.insert_one(query)
    return redirect("/airline_registration?message=Airline Added Successfully")

@app.route("/airline_home")
def airline_home():
    return render_template("airline_home.html")

@app.route("/logout")
def logout():
    return redirect("/")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/locations")
def locations():
    query={}
    locations=locations_collection.find(query)
    locations=list(locations)
    message=request.args.get("message")
    return render_template("locations.html",locations=locations,message=message)

@app.route("/locations_action",methods=['post'])
def locations_action():
    location=request.form.get("location")
    query={"location":location}
    count=locations_collection.count_documents(query)
    if count>0:
        return redirect("/locations?message=duplicate location")
    query = {"location": location}
    locations_collection.insert_one(query)
    return redirect("/locations?message=location added successfully")

@app.route("/airports")
def airports():
    query = {}
    locations = locations_collection.find(query)
    locations = list(locations)
    query={}
    airports=airports_collection.find(query)
    airports=list(airports)
    message=request.args.get("message")
    return render_template("airports.html",locations=locations,airports=airports,message=message,get_airports_by_location_id=get_airports_by_location_id)

@app.route("/airport_action",methods=['post'])
def airport_action():
    airport=request.form.get("airport")
    airport_type=request.form.get("airport_type")
    location_id=request.form.get("location_id")
    query={"airport":airport}
    count=airports_collection.count_documents(query)
    if count>0:
        return redirect("/airports?message=duplicate airport name")
    query={"airport":airport,"airport_type":airport_type,"location_id":ObjectId(location_id)}
    airports_collection.insert_one(query)
    return redirect("/airports?message=airport added successfully")

def get_airports_by_location_id(location_id):
    query={"location_id":ObjectId(location_id)}
    airports=airports_collection.find(query)
    airports=list(airports)
    return airports

@app.route("/add_airplane")
def add_airplane():
    airline_id = session["airline_id"]
    query = {"airline_id":ObjectId(airline_id)}
    airplanes = airplanes_collection.find(query)
    airplanes = list(airplanes)
    return render_template("add_airplane.html",airplanes=airplanes,get_airline_by_airline_id=get_airline_by_airline_id)

@app.route("/add_airplane_action",methods=['post'])
def add_airplane_action():
    airplane_name=request.form.get("airplane_name")
    airplane_number=request.form.get("airplane_number")
    description=request.form.get("description")
    economy_class_available_seats=request.form.get("economy_class_available_seats")
    business_class_available_seats=request.form.get("business_class_available_seats")
    first_class_available_seats=request.form.get("first_class_available_seats")
    airline_id= session['airline_id']
    image=request.files.get("image")
    path=profiles+"/"+image.filename
    image.save(path)
    query={"airplane_name":airplane_name,"airplane_number":airplane_number,"image":image.filename,"description":description,"economy_class_available_seats":economy_class_available_seats,"business_class_available_seats":business_class_available_seats,"first_class_available_seats":first_class_available_seats,"airline_id":ObjectId(airline_id)}
    airplanes_collection.insert(query)
    return render_template("apmessage.html",message="airplane added successfully")

def get_airline_by_airline_id(airline_id):
    query={"_id":airline_id}
    airline=airlines_collection.find_one(query)
    return airline

@app.route("/add_schedule")
def add_schedule():
    airplane_id=request.args.get("airplane_id")
    airports=airports_collection.find({})
    airports=list(airports)
    message=request.args.get("message")
    today = datetime.datetime.now()
    today = today.strftime("%Y-%m-%dT%H:%M")
    return render_template("add_schedule.html",airplane_id=airplane_id,airports=airports,message=message,today=today)

@app.route("/schedules_action",methods=['post'])
def schedules_action():
    airplane_id=request.form.get("airplane_id")
    print(airplane_id)
    arrival_date_time=request.form.get("arrival_date_time")
    departure_date_time=request.form.get("departure_date_time")
    business_class_price=request.form.get("business_class_price")
    economic_class_price=request.form.get("economic_class_price")
    first_class_price=request.form.get("first_class_price")
    source_airport_id=request.form.get("source_airport_id")
    print(source_airport_id)
    destination_airport_id=request.form.get("destination_airport_id")
    print(destination_airport_id)
    departure_date_time=datetime.datetime.strptime(departure_date_time,"%Y-%m-%dT%H:%M")
    arrival_date_time = datetime.datetime.strptime(arrival_date_time, "%Y-%m-%dT%H:%M")
    today=datetime.datetime.now()
    if departure_date_time<today:
        return redirect("/add_schedule?message=you can not add schedule for past dates")
    if arrival_date_time<departure_date_time:
        return redirect("/add_schedule?message=departure date should be greater than arrival date")
    diff = arrival_date_time - departure_date_time
    print(diff.days)
    hours = int(diff.seconds / 3600)
    mins = int(diff.seconds % 3600 / 60)
    duration = ""
    if diff.days > 0:
        hours = hours + (diff.days * 24)
    if hours != 0:
        duration = str(hours) + " hours "
    if mins != 0:
        duration = duration + str(mins) + " Minutes"
    print(duration)
    departure_date=departure_date_time.strftime("%Y-%m-%d")
    departure_date=datetime.datetime.strptime(departure_date,"%Y-%m-%d")
    query={"$or":[{"departure_date_time":{"$gte":departure_date_time,
                                          "$lte":arrival_date_time},
                      "arrival_date_time":{"$gte":arrival_date_time},"airplane_id":ObjectId(airplane_id)},
                   {"departure_date_time":{"$lte":departure_date_time},
                    "arrival_date_time":{"$gte":departure_date_time,
                                         "$lte":arrival_date_time},"airplane_id":ObjectId(airplane_id)},
                    {"departure_date_time":{"$lte":departure_date_time},
                     "arrival_date_time":{"$gte":arrival_date_time},"airplane_id":ObjectId(airplane_id)},
                   {"departure_date_time":{"$gte":departure_date_time,
                                          "$lte":arrival_date_time},
                   "arrival_date_time":{"$gte":departure_date_time,
                                          "$lte":arrival_date_time},"airplane_id":ObjectId(airplane_id)}
    ]}
    count=schedules_collection.count_documents(query)
    if count!=0:
        return render_template("apmessage.html",message="time collision occurred")
    query={"arrival_date_time":arrival_date_time,"departure_date_time":departure_date_time,"business_class_price":business_class_price,"economic_class_price":economic_class_price,"first_class_price":first_class_price,"duration":str(duration),"source_airport_id":ObjectId(source_airport_id),"destination_airport_id":ObjectId(destination_airport_id),"airplane_id":ObjectId(airplane_id),"departure_date":departure_date}
    schedules_collection.insert(query)
    return render_template("apmessage.html",message="schedule added successfully")

@app.route("/view_schedule")
def view_schedule():
    airplane_id=request.args.get("airplane_id")
    today=datetime.datetime.now()
    query={"airplane_id":ObjectId(airplane_id),"departure_date_time":{"$gte":today}}
    print(query)
    future_schedules=schedules_collection.find(query)
    future_schedules=list(future_schedules)
    query = {"airplane_id": ObjectId(airplane_id), "departure_date_time": {"$lte": today}}
    past_schedules=schedules_collection.find(query)
    past_schedules=list(past_schedules)
    message=request.args.get("message")
    future_schedules.reverse()
    past_schedules.reverse()
    return render_template("view_schedule.html",message=message,future_schedules=future_schedules,past_schedules=past_schedules,get_source_airport_name_by_airport_id=get_source_airport_name_by_airport_id,get_airplane_name_by_airplane_id=get_airplane_name_by_airplane_id,get_destination_airport_name_by_airport_id=get_destination_airport_name_by_airport_id,len=len)

def get_source_airport_name_by_airport_id(airport_id):
    query={"_id":airport_id}
    airport= airports_collection.find_one(query)
    print(airport)
    return airport

def get_destination_airport_name_by_airport_id(airport_id):
    query={"_id":airport_id}
    airport= airports_collection.find_one(query)
    print(airport)
    return airport

def get_airplane_name_by_airplane_id(airplane_id):
    query={"_id":airplane_id}
    airplane=airplanes_collection.find_one(query)
    print(airplane)
    return airplane

def get_source_location_by_airport_id(location_id):
    query={"_id":location_id}
    location=locations_collection.find_one(query)
    print(location)
    return location

def get_destination_location_by_airport_id(location_id):
    query={"_id":location_id}
    location=locations_collection.find_one(query)
    print(location)
    return location

def get_seats_by_airplane_id(airplane_id):
    query={"_id":airplane_id}
    airplane=airplanes_collection.find_one(query)
    return airplane

@app.route("/search_flights")
def search_flights():
    locations=locations_collection.find({})
    locations=list(locations)
    source_location_id = request.args.get("source_location_id")
    destination_location_id = request.args.get("destination_location_id")
    date = request.args.get("date")
    print(destination_location_id)
    if source_location_id == None:
        source_location_id == ""
    if destination_location_id == None:
        destination_location_id = ""
    if date == None:
        date = datetime.datetime.now()
    if source_location_id == "" or destination_location_id == "" or date == "":
        query = {"abc":"abc"}
    else:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        print(date)
        query = {"location_id": ObjectId(source_location_id)}
        source_airports = airports_collection.find(query)
        source_airports = list(source_airports)
        query = {"location_id": ObjectId(destination_location_id)}
        destination_airports = airports_collection.find(query)
        destination_airports = list(destination_airports)
        source_airport_ids = []
        for source_airport in source_airports:
            source_airport_ids.append(source_airport['_id'])
        destination_airport_ids = []
        for destination_airport in destination_airports:
            destination_airport_ids.append(destination_airport['_id'])
        today = datetime.datetime.now()
        query = {"departure_date": date, "source_airport_id": {"$in": source_airport_ids},
                 "destination_airport_id": {"$in": destination_airport_ids}, "departure_date_time": {"$gte":today} }
    print(query)
    schedules = schedules_collection.find(query)
    schedules = list(schedules)
    print(schedules)
    date = date.strftime("%Y-%m-%d")
    return render_template("search_flights.html",locations=locations,schedules=schedules,get_source_airport_name_by_airport_id=get_source_airport_name_by_airport_id,get_destination_airport_name_by_airport_id=get_destination_airport_name_by_airport_id,get_airplane_name_by_airplane_id=get_airplane_name_by_airplane_id,get_source_location_by_airport_id=get_source_location_by_airport_id,get_destination_location_by_airport_id=get_destination_location_by_airport_id,get_seats_by_airplane_id=get_seats_by_airplane_id,str=str, source_location_id=source_location_id, destination_location_id=destination_location_id, date=date)

@app.route("/book_ticket")
def book_ticket():
    schedule_id=request.args.get("schedule_id")
    class_type=request.args.get("class_type")
    query={"_id":ObjectId(schedule_id)}
    schedule=schedules_collection.find_one(query)
    total_seats=request.args.get("total_seats")
    total_seats=int(total_seats)
    return render_template("book_ticket.html",schedule_id=schedule_id,schedule=schedule,class_type=class_type,get_source_airport_name_by_airport_id=get_source_airport_name_by_airport_id,get_destination_airport_name_by_airport_id=get_destination_airport_name_by_airport_id,get_airplane_name_by_airplane_id=get_airplane_name_by_airplane_id,get_source_location_by_airport_id=get_source_location_by_airport_id,get_destination_location_by_airport_id=get_destination_location_by_airport_id,get_seats_by_airplane_id=get_seats_by_airplane_id,total_seats=total_seats, is_seat_booked_by_seat_number_and_schedule_id_and_class_type=is_seat_booked_by_seat_number_and_schedule_id_and_class_type)

@app.route("/book_tickets2")
def book_tickets2():
    schedule_id = request.args.get("schedule_id")
    class_type = request.args.get("class_type")
    total_seats = request.args.get("total_seats")
    selected_seats=[]
    for i in range(1,int(total_seats)+1):
        seat=request.args.get("seat"+str(i))
        if seat!=None:
            selected_seats.append(i)
    if len(selected_seats)==0:
        return render_template("cmessage.html",message="please select seats")
    query={"_id":ObjectId(schedule_id)}
    schedule=schedules_collection.find_one(query)
    if class_type == 'first_class':
        total_price = int(schedule['first_class_price'])*len(selected_seats)
    if class_type == 'economy_class':
        total_price = int(schedule['economic_class_price'])*len(selected_seats)
    if class_type == 'business_class':
        total_price = int(schedule['business_class_price'])*len(selected_seats)
    return render_template("book_tickets2.html",schedule=schedule,selected_seats=selected_seats,schedule_id=schedule_id,class_type=class_type,total_seats=total_seats, total_price=total_price)

@app.route("/book_tickets3")
def book_tickets3():
    customer_id=session['customer_id']
    schedule_id=request.args.get("schedule_id")
    class_type=request.args.get("class_type")
    total_seats=request.args.get("total_seats")
    total_price=request.args.get("total_price")
    booking_date=datetime.datetime.now()
    query={"status":"Payment Pending", "schedule_id":ObjectId(schedule_id),"class_type":class_type, "customer_id":ObjectId(customer_id),"booking_date":booking_date,"total_price":total_price}
    result=bookings_collection.insert_one(query)
    booking_id=result.inserted_id
    seat_numbers = []
    for i in range(1,int(total_seats)+1):
        seat_number=request.args.get("seat_number"+str(i))
        if seat_number != None:
            name=request.args.get("name"+str(i))
            age=request.args.get("age"+str(i))
            phone=request.args.get("phone"+str(i))
            gender=request.args.get("gender"+str(i))
            query={"seat_number":seat_number,"name":name,"phone":phone,"age":age,"gender":gender,"customer_id":ObjectId(customer_id),"booking_id":booking_id}
            boarding_pass_collection.insert_one(query)
            seat_numbers.append(i)
    query = {"_id":booking_id}
    query2 = {"$set": {"seat_numbers": seat_numbers}}
    bookings_collection.update_one(query, query2)
    booking=bookings_collection.find_one(query)
    query={"booking_id":booking_id}
    boarding_passes=boarding_pass_collection.find(query)
    boarding_passes=list(boarding_passes)
    return render_template("book_tickets3.html",booking_id=booking_id,booking=booking,boarding_passes=boarding_passes,total_price=total_price)

@app.route("/payments")
def payments():
    amount=request.args.get("total_price")
    card_number=request.args.get("card_number")
    card_type=request.args.get("card_type")
    card_holder_name=request.args.get("card_holder_name")
    cvv=request.args.get("cvv")
    expiry_date=request.args.get("expiry_date")
    booking_id=request.args.get("booking_id")
    print(booking_id)
    customer_id=session['customer_id']
    payment_date=datetime.datetime.now()
    query={"amount":amount,"status":"payment success","card_number":card_number,"card_type":card_type,"card_holder_name":card_holder_name,"cvv":cvv,"expiry_date":expiry_date,"payment_date":payment_date,"booking_id":ObjectId(booking_id),"customer_id":ObjectId(customer_id)}
    payments_collection.insert_one(query)
    query1={"_id":ObjectId(booking_id)}
    print(query1)
    query2={"$set":{"status":"Booked"}}
    print(query2)
    bookings_collection.update_one(query1,query2)
    return render_template("payments.html",message="Booking Success")

@app.route("/bookings")
def bookings():
    schedule_id=request.args.get("schedule_id")
    class_type=request.args.get("class_type")
    if session['role']=='customer':
        customer_id=session['customer_id']
        query={"customer_id":ObjectId(customer_id), "status": {"$ne": "Payment Pending"}}
    else:
        query={"schedule_id":ObjectId(schedule_id),"class_type":class_type, "status": {"$ne": "Payment Pending"}}
    bookings=bookings_collection.find(query)
    bookings=list(bookings)
    bookings.reverse()
    return render_template("bookings.html",bookings=bookings,get_source_airport_name_by_airport_id=get_source_airport_name_by_airport_id,get_destination_airport_name_by_airport_id=get_destination_airport_name_by_airport_id,get_airplane_name_by_airplane_id=get_airplane_name_by_airplane_id,get_source_location_by_airport_id=get_source_location_by_airport_id,get_destination_location_by_airport_id=get_destination_location_by_airport_id,get_seats_by_airplane_id=get_seats_by_airplane_id,get_schedule_by_schedule_id=get_schedule_by_schedule_id,get_customer_by_customer_id=get_customer_by_customer_id,get_boarding_pass_by_booking_id=get_boarding_pass_by_booking_id,diff_hours_from_today_and_departure_time=diff_hours_from_today_and_departure_time, int=int,get_payment_details_by_booking_id=get_payment_details_by_booking_id)

def get_schedule_by_schedule_id(schedule_id):
    query={"_id":schedule_id}
    schedule=schedules_collection.find_one(query)
    return schedule

def get_customer_by_customer_id(customer_id):
    query={"_id":customer_id}
    customer=customers_collection.find_one(query)
    return customer

@app.route("/view_payments")
def view_payments():
    booking_id=request.args.get("booking_id")
    query={"booking_id":ObjectId(booking_id)}
    print(query)
    payment=payments_collection.find_one(query)
    return render_template("view_payments.html",payment=payment)

@app.route("/cancel")
def cancel():
    booking_id=request.args.get("booking_id")
    payment_id=request.args.get("payment_id")
    refund_amount=request.args.get("refund_amount")
    print(refund_amount)
    print(booking_id)
    query1 = {'_id': ObjectId(booking_id)}
    print(query1)
    query2 = {"$set": {"status": "Cancelled"}}
    print(query2)
    bookings_collection.update_one(query1, query2)
    query3={'_id':ObjectId(payment_id)}
    query4={"$set":{"status":"90% refunded","amount":refund_amount}}
    payments_collection.update_one(query3,query4)
    return redirect("/bookings")

def get_payment_details_by_booking_id(booking_id):
    query={"booking_id":booking_id}
    payment=payments_collection.find_one(query)
    return payment

def get_boarding_pass_by_booking_id(booking_id):
    query={"booking_id":booking_id}
    boarding_passes=boarding_pass_collection.find(query)
    boarding_passes=list(boarding_passes)
    return boarding_passes

@app.route("/boarding_pass")
def boarding_pass():
    booking_id=request.args.get("booking_id")
    query={"booking_id":ObjectId(booking_id)}
    boarding_passes=boarding_pass_collection.find(query)
    boarding_passes=list(boarding_passes)
    query={"_id":ObjectId(booking_id)}
    booking=bookings_collection.find_one(query)
    return render_template("boarding_pass.html",boarding_passes=boarding_passes,booking=booking,get_source_airport_name_by_airport_id=get_source_airport_name_by_airport_id,get_destination_airport_name_by_airport_id=get_destination_airport_name_by_airport_id,get_airplane_name_by_airplane_id=get_airplane_name_by_airplane_id,get_source_location_by_airport_id=get_source_location_by_airport_id,get_destination_location_by_airport_id=get_destination_location_by_airport_id,get_seats_by_airplane_id=get_seats_by_airplane_id,get_schedule_by_schedule_id=get_schedule_by_schedule_id,get_customer_by_customer_id=get_customer_by_customer_id)

def is_seat_booked_by_seat_number_and_schedule_id_and_class_type(seat_number, schedule_id, class_type):
    query = {"seat_numbers": seat_number,"schedule_id": ObjectId(schedule_id), "class_type": class_type, "status": "Booked"}
    count = bookings_collection.count_documents(query)
    if count > 0:
        return True
    return False

def diff_hours_from_today_and_departure_time(departure_date_time):
    today=datetime.datetime.now()
    diff=departure_date_time-today
    if today>departure_date_time:
        return "",0
    hours=int(diff.seconds/3600)
    days=diff.days
    min=int((diff.seconds%3600)/60)
    diff_str=""
    if days!=0:
        diff_str=str(days)+" days "
    if hours!=0:
        diff_str=diff_str+str(hours)+" hours "
    if min!=0:
        diff_str=diff_str+str(min)+" minutes "
    hours=(24*days)+hours
    return diff_str,hours

app.run(debug=True)