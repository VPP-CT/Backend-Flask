@app.route('/packages')
def packages():
    flight_data = flight_data_obj()
    flight_data.budget = request.args.get('budget')
    flight_data.seg = request.args.get('seg')
    flight_data.orig = []
    flight_data.dest = []
    flight_data.date = []
    for x in range(1, int(flight_data.seg) + 1):
        flight_data.orig.append(request.args.get('origin%d' % x))
        flight_data.dest.append(request.args.get('dest%d' % x))
        flight_data.date.append(request.args.get('date%d' % x))

    slice = [dict(origin=flight_data.orig[x], destination=flight_data.dest[x],
                  date=flight_data.date[x]) for x in range(0, int(flight_data.seg))]
    data = {
        "request": {
            "slice": slice,
            "passengers": dict(adultCount=1),
            "refundable": 'false'
        }
    }
    flight_result = flight_parser.get_flights(data)
    # flight_result = json.dumps(flight_results)
    # return jsonify(flight_result)
    package_data = dict()
    for y in range(3):
        package_data['flight%d' % y] = flight_result['option0']
        hotel_results = dict()
        for x in range(len(flight_result['option0']['trips']) - 1):
            trip_cur = flight_result['option0']['trips']['trip%d' % x]
            trip_next = flight_result['option0']['trips']['trip%d' % (x + 1)]
            hotel_data = hotel_data_obj()
            hotel_data.checkin_date = trip_cur['stop%d' %(len(trip_cur) - 1)]['arrivalTime'][:10]
            hotel_data.checkout_date = trip_next['stop0']['departureTime'][:10]
            location = geo.geocode(request.args.get('dest%d' % x))
            hotel_data.latitude = location.latitude
            hotel_data.longitude = location.longitude
            hotel_result = hotel_parser.search_hotels(hotel_data)
            hotel_results['trip%d' % x] = hotel_result['hotel_list']['hotel%d' % y]
        package_data['hotel%d' % y] = hotel_results
    return jsonify(package_data)