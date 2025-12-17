class FitnessClass:
    def __init__(self, title, instructor, capacity, date_time, base_price):
        """
        Fitness dersini temsil eder.
        :param capacity: Maksimum katılımcı sayısı
        :param base_price: Taban fiyat (TL)
        """
        self.title = title
        self.instructor = instructor
        self.capacity = capacity
        self.date_time = date_time
        self.base_price = base_price
        
        # Rezervasyon yapan üyelerin ID'lerini burada tutacağız
        self.reservations = []

    def current_occupancy(self):
        """Şu anki doluluk sayısını döner."""
        return len(self.reservations)