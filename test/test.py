from main import create_ical, Residence

residences = [
    Residence(name="浅草A邸",
              arrival_date="到着日：2021年12月18日（土）",
              arrival_time="到着時間：19:00",
              departure_date="出発日：2021年12月19日（日）",
              ),
    Residence(name="浅草A邸",
              arrival_date="到着日：2021年12月20日（月）",
              arrival_time="到着時間：14:00",
              departure_date="出発日：2021年12月24日（金）",
              ),
    Residence(name="浅草A邸",
              arrival_date="到着日：2021年12月24日（金）",
              arrival_time="到着時間：17:00",
              departure_date="出発日：2021年12月28日（火）",
              ),
]


def test_create_ical():
    ical = create_ical(residences)
    print(ical.to_ical())