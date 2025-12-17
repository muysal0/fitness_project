def calculate_price(fitness_class, member):
    """
    Dinamik fiyatlandırma kurallarını uygular.
    1. Base price alınır.
    2. Öğrenci indirimi uygulanır.
    3. Doluluk oranına göre (Surge Pricing) zam uygulanır.
    """
    price = fitness_class.base_price

    # KURAL 1: Öğrenci İndirimi (%20)
    if member.membership_type == "student":
        price = price * 0.80

    # KURAL 2: Surge Pricing (Yoğunluk Zammı)
    # Eğer kapasite 0 ise (hata olmasın diye) doluluk 0 kabul edilir
    if fitness_class.capacity > 0:
        occupancy_rate = fitness_class.current_occupancy() / fitness_class.capacity
        
        # Eğer doluluk %80'den (0.80) fazlaysa %20 zam yap
        if occupancy_rate > 0.80:
            price = price * 1.20

    return price