def calculate_price(fitness_class, member):
    """
    Dinamik fiyatlandırma kuralları.
    1. Base price alınır.
    2. Öğrenci indirimi (%50) uygulanır.
    3. Doluluk %80 üzerindeyse %20 zam (Surge) uygulanır.
    """
    price = fitness_class.base_price

    # KURAL 1: Öğrenci İndirimi (%50) -- (Eskiden 0.80 idi, 0.50 yaptık)
    if member.membership_type == "student":
        price = price * 0.50

    # KURAL 2: Surge Pricing (Yoğunluk Zammı)
    if fitness_class.capacity > 0:
        occupancy_rate = fitness_class.current_occupancy() / fitness_class.capacity
        
        # Doluluk %80'den fazlaysa %20 zam
        if occupancy_rate > 0.80:
            price = price * 1.20

    return round(price, 2)