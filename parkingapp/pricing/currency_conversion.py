

def mkd_to_eur_cents(mkd_amount):
    EUR_TO_MKD = 1/61.5
    eur = mkd_amount*EUR_TO_MKD
    return int(round(eur*100))
