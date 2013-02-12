month = get_month_from_form()
year = get_year_from_form()
day_count = get_day_count(month, year)

month = prepend_zero(month)

query_params = {'start_time': '2013-%s-01 00:00:00' % month,
                'end_time': '2013-%s-%s 23:59:59' % (month, day_count)}

meter = api.get_meter(meter_id)
records = api.get_host_meter_records(host_id, meter_id, query_params)


buckets = {}
for d in range(1,day_count+1):
    d = prepend_zero(d)
    buckets[d] = []

# gather values
for r in records:
    day = get_day_from_timestamp(r.timestamp)
    day = prepend_zero(day)
    value = cast(r.value, meter.data_type)
    if day in buckets:
        buckets[day].append(value)

# calculate averages
averages = {}
for day in buckets:
    averages[day] = avg(buckets[day])

return averages