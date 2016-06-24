from umalqurra.hijri_date import HijriDate
from datetime import datetime, timedelta
from collections import namedtuple
import pytz

from django.conf import settings


DateRange = namedtuple('DateRange', ['start', 'end'])
# ranges: array of DateRange's for the date setting
HijriDateSet = namedtuple('HijriDateSet', ['key', 'label', 'ranges'])
local_tz = pytz.timezone(settings.TIME_ZONE)


def hijri_to_gregorian(umalqurra_date):
    """Convert a HijriDate to a python datetime

    Args:
        umalqurra_date (HijriDate): date to convert
    Return:
        datetime.datetime
    """
    day = umalqurra_date.day_gr
    month = umalqurra_date.month_gr
    year = umalqurra_date.year_gr
    gregorian_date = datetime(int(year), int(month), int(day))
    return gregorian_date


def gregorian_to_hijri(gregorian_date):
    """Convert a python datetime to a HijriDate

    Args:
        gregorian_date (datetime): date to convert
    Returns:
        ummalqurra.hijri_date.HijriDate
    """
    day = gregorian_date.day
    month = gregorian_date.month
    year = gregorian_date.year
    umalqurra_date = HijriDate(year, month, day, gr=True)
    return umalqurra_date


def hijri_day_range(min_date, max_date, periodic=False):
    """
    Returns one set for each day in the range
    If periodic is set to True, then it uses the day of month (31 days)

    Args:
        min_date (date): gregorian date to start the date range at
        max_date (date): gregorian date to end the date range at
        periodic (boolean): whether the date range should be periodic over the month
                            (day of week aggregation isn't handled in hijri since it
                             is the same in both calendars)
    Returns:
        {'type': 'days', 'bounds': bounds, 'date_sets': days, 'periodic': periodic}
             bounds: bounding DateRange which the date sets contain
             days: array of HijriDateSets
    """
    min_date = datetime.combine(min_date, datetime.min.time())
    max_date = datetime.combine(max_date, datetime.min.time())
    hijri_min_date = gregorian_to_hijri(min_date)
    hijri_max_date = gregorian_to_hijri(max_date)
    bounds = DateRange(start=min_date, end=max_date)
    years = xrange(int(hijri_min_date.year), int(hijri_max_date.year) + 1)
    days = []
    if periodic:
        days = [
            HijriDateSet(
                key=str(day),
                label=[{'text': str(day), 'translate': False}],
                ranges=[]
            )
            for day in xrange(1, 31)
        ]

    for year in years:
        max_month = 12
        if hijri_max_date.year == year:
            max_month = int(hijri_max_date.month)
        for month in xrange(int(hijri_min_date.month), max_month + 1):
            start_date_um = HijriDate(year, month, 1)
            if hijri_to_gregorian(hijri_min_date) > hijri_to_gregorian(start_date_um):
                start_date_um = hijri_min_date

            end_year = year
            end_month = month + 1
            if end_month >= 12:
                end_year = year+1
                end_month = 1

            end_date_um = HijriDate(end_year, end_month, 1)
            end_year_gr = int(end_date_um.year_gr)
            end_month_gr = int(end_date_um.month_gr)
            end_day_gr = int(end_date_um.day_gr)
            end_date_gr = datetime(end_year_gr, end_month_gr, end_day_gr)
            delta = timedelta(days=1)
            last_date_gr = end_date_gr - delta
            last_date_um = HijriDate(
                last_date_gr.year, last_date_gr.month, last_date_gr.day, gr=True
            )
            if hijri_to_gregorian(hijri_max_date) < hijri_to_gregorian(last_date_um):
                last_date_um = hijri_max_date

            for day in xrange(int(start_date_um.day), int(last_date_um.day) + 1):
                hijri_day = HijriDate(year, month, day)
                hijri_year_gr = int(hijri_day.year_gr)
                hijri_month_gr = int(hijri_day.month_gr)
                hijri_day_gr = int(hijri_day.day_gr)
                greg_day = datetime(hijri_year_gr, hijri_month_gr, hijri_day_gr)
                next_greg_day = greg_day + delta

                day_range = DateRange(start=local_tz.localize(greg_day),
                                      end=local_tz.localize(next_greg_day))
                if periodic:
                    days[day-1].ranges.append(day_range)
                else:
                    days.append(
                        HijriDateSet(
                            key='{}/{}/{}'.format(
                                int(hijri_day.day), int(hijri_day.month), int(hijri_day.year)
                            ),
                            label=[
                                {
                                    'text': u'{} {}\u060c {}'.format(  # arabic comma
                                        int(hijri_day.day),
                                        hijri_day.month_name.decode('utf-8'),
                                        int(hijri_day.year)
                                    ),
                                    'translate': False
                                }
                            ],
                            ranges=[day_range]
                        )
                    )

    return {'type': 'days', 'bounds': bounds, 'date_sets': days, 'periodic': periodic}


def hijri_week_range(min_date, max_date, periodic=False):
    """Get an array of start and end dates for each week in the given gregorian date range.

    Date ranges have an inclusive start date and exclusive end date
    There is no sequential parameter for this function - sequential ranges are the same for
    both the gregorian and hijri calendar.

    Args:
        min_date (date): gregorian date to start the date range at
        max_date (date): gregorian date to end the date range at
        periodic (boolean): whether the date range should be periodic over the year

    Returns:
        {'type': 'weeks', 'bounds': bounds, 'date_sets': days, 'periodic': periodic}
             bounds: bounding DateRange which the date sets contain
             days: array of HijriDateSets
    """
    def _hijri_day_of_year(date):
        date_um = gregorian_to_hijri(date)
        first_day_of_year_um = HijriDate(date_um.year, 1, 1)
        first_day_of_year_gr = hijri_to_gregorian(first_day_of_year_um)
        tdiff = date - first_day_of_year_gr
        day_of_year = tdiff.days + 1
        return day_of_year

    def _hijri_week_of_year(date):
        date_um = gregorian_to_hijri(date)
        first_day_of_year_um = HijriDate(date_um.year, 1, 1)
        first_day_of_year_gr = hijri_to_gregorian(first_day_of_year_um)
        tdiff = date - first_day_of_year_gr
        day_of_year = tdiff.days + 1
        date_dow = date.isoweekday()
        first_day_dow = first_day_of_year_gr.isoweekday()
        weeknum = ((day_of_year + 6)/7)
        if date_dow < first_day_dow:
            weeknum += 1
        return weeknum

    # get years over which to aggregate
    bounds = DateRange(start=min_date, end=max_date)
    min_date = datetime.combine(min_date, datetime.min.time())
    max_date = datetime.combine(max_date, datetime.min.time())
    weeks = []
    if periodic:
        weeks = [
            HijriDateSet(
                key=str(week),
                label=[
                    {
                        'text': 'AGG.WEEK',
                        'translate': True
                    },
                    {
                        'text': str(week),
                        'translate': False
                    }
                ],
                ranges=[]
            )
            for week in xrange(0, 52)
        ]
    num_weeks = ((max_date - min_date) / 7).days
    min_date_dow = min_date.isoweekday()
    if min_date_dow > 0:
        num_weeks += 1

    if min_date_dow == 0:
        start_of_first_week = min_date
        start_of_first_week_gr = hijri_to_gregorian(start_of_first_week)
    else:
        start_of_first_week_gr = min_date - timedelta(days=min_date_dow)
        start_of_first_week = gregorian_to_hijri(start_of_first_week_gr)
    for week in xrange(0, num_weeks):
        week_start_gr = start_of_first_week_gr + timedelta(days=(7*week))
        week_start_um = gregorian_to_hijri(week_start_gr)
        week_end_gr = week_start_gr + timedelta(days=7)
        week_range = DateRange(start=local_tz.localize(week_start_gr),
                               end=local_tz.localize(week_end_gr))
        if periodic:
            week_um = _hijri_week_of_year(week_start_gr)
            weeks[week_um].ranges.append(week_range)
        else:
            week_of_year = _hijri_week_of_year(week_start_gr)
            weeks.append(
                HijriDateSet(
                    key=u'{} Week {}'.format(
                        int(week_start_um.year), week_of_year
                    ),
                    label=[
                        {
                            'text': str(int(week_start_um.year)),
                            'translate': False
                        },
                        {
                            'text': 'AGG.WEEK',
                            'translate': True
                        },
                        {
                            'text': str(week_of_year)
                        }
                    ],
                    ranges=[week_range]
                )
            )
    return {'type': 'weeks', 'bounds': bounds, 'date_sets': weeks, 'periodic': False}


def hijri_month_range(min_date, max_date, periodic=False):
    """Get an array of start and end dates for each month in the given gregorian date range.

    Date ranges have an inclusive start and exclusive end date.

    Note:
    calculate start of month as the first day of the month, converted to gregorian
    calculate end of month as the first day of the next month, converted to gregorian
    Any ranges should use GTE start, LT end

    Returns all 12 months for periodic, even if they don't have a date range

    Args:
        min_date (date): gregorian date to start the date range at
        max_date (date): gregorian date to end the date range at
        periodic (boolean): whether the date range should be periodic over the year

    Returns:
        {'type': 'months', 'bounds': bounds, 'date_sets': days, 'periodic': periodic}
             bounds: bounding DateRange which the date sets contain
             days: array of HijriDateSets
    """
    min_date = datetime.combine(min_date, datetime.min.time())
    max_date = datetime.combine(max_date, datetime.min.time())
    hijri_min_date = gregorian_to_hijri(min_date)
    hijri_max_date = gregorian_to_hijri(max_date)
    bounds = DateRange(start=min_date, end=max_date)
    years = xrange(int(hijri_min_date.year), int(hijri_max_date.year) + 1)
    months = []

    min_month = int(hijri_min_date.month)

    if periodic:
        months = [
            HijriDateSet(key=month_num,
                         label=[{
                             'text': month,
                             'translate': False
                         }],
                         ranges=[])
            for month, month_num in [
                    (HijriDate(1437, x, 1).month_name.decode('utf-8'), x) for x in xrange(1, 13)
            ]
        ]
        min_month = 1

    for year in years:
        for month in xrange(min_month, 13):
            start_date_um = HijriDate(year, month, 1)
            start_year_gr = int(start_date_um.year_gr)
            start_month_gr = int(start_date_um.month_gr)
            start_day_gr = int(start_date_um.day_gr)
            start_date_gr = datetime(start_year_gr, start_month_gr, start_day_gr)

            end_year = year
            end_month = month + 1
            if end_month > 12:
                end_year = year+1
                end_month = 1

            end_date_um = HijriDate(end_year, end_month, 1)
            end_year_gr = int(end_date_um.year_gr)
            end_month_gr = int(end_date_um.month_gr)
            end_day_gr = int(end_date_um.day_gr)
            end_date_gr = datetime(end_year_gr, end_month_gr, end_day_gr)

            month_range = DateRange(start=local_tz.localize(start_date_gr),
                                    end=local_tz.localize(end_date_gr))
            if periodic:
                months[month-1].ranges.append(month_range)
            else:
                if max_date < hijri_to_gregorian(HijriDate(year, month, 1)):
                    break
                months.append(
                    HijriDateSet(
                        key=month,
                        label=[{
                            'text': u'{} {}'.format(
                                start_date_um.month_name.decode('utf-8'),
                                int(start_date_um.year)
                            ),
                            'translate': False
                        }],
                        ranges=[month_range]
                    )
                )
        min_month = 1  # reset min_month to 1, it should only limit the first year
    return {'type': 'months', 'bounds': bounds, 'date_sets': months, 'periodic': periodic}


def hijri_year_range(min_date, max_date):
    """Get an array of start and end dates for each year in the given gregorian date ranges

    There is no periodic year range

    Args:
        min_date (date): gregorian date to start the date range at
        max_date (date): gregorian date to end the date range at

    Returns:
        {'type': 'years', 'bounds': bounds, 'date_sets': days, 'periodic': periodic}
             bounds: bounding DateRange which the date sets contain
             days: array of HijriDateSets
    """
    min_date = datetime.combine(min_date, datetime.min.time())
    max_date = datetime.combine(max_date, datetime.min.time())
    hijri_min_date = gregorian_to_hijri(min_date)
    hijri_max_date = gregorian_to_hijri(max_date)
    bounds = DateRange(start=min_date, end=max_date)
    hijri_years = xrange(int(hijri_min_date.year), int(hijri_max_date.year) + 1)
    years = []
    for year in hijri_years:
        start_date_um = HijriDate(year, 1, 1)
        start_year_gr = int(start_date_um.year_gr)
        start_month_gr = int(start_date_um.month_gr)
        start_day_gr = int(start_date_um.day_gr)
        start_date_gr = datetime(start_year_gr, start_month_gr, start_day_gr)

        end_date_um = HijriDate(year + 1, 1, 1)
        end_year_gr = int(end_date_um.year_gr)
        end_month_gr = int(end_date_um.month_gr)
        end_day_gr = int(end_date_um.day_gr)
        end_date_gr = datetime(end_year_gr, end_month_gr, end_day_gr)

        years.append(
            HijriDateSet(
                key=str(year),
                label=[{
                    'text': str(year),
                    'translate': False
                }],
                ranges=[DateRange(
                    start=local_tz.localize(start_date_gr), end=local_tz.localize(end_date_gr)
                )]
            )
        )
    return {'type': 'years', 'bounds': bounds, 'date_sets': years, 'periodic': False}
