class ReservationManager:
    def book_class(self, member, fitness_class):
        """
        Üyeyi derse kaydeder.
        Önce kapasite kontrolü yapar.
        """
        # 1. Kapasite Kontrolü
        if fitness_class.current_occupancy() >= fitness_class.capacity:
            raise ValueError("Class is full")

        # 2. Rezervasyon İşlemi
        # Üyenin ID'sini dersin rezervasyon listesine ekliyoruz
        fitness_class.reservations.append(member.member_id)

        # 3. Onay Mesajı Dönüyoruz
        return {
            "status": "confirmed",
            "member_id": member.member_id,
            "class_title": fitness_class.title,
            "message": "Reservation successful"
        }

    def cancel_reservation(self, member, fitness_class):
        """
        Rezervasyonu iptal eder (Ekstra özellik, PDF'te var).
        """
        if member.member_id in fitness_class.reservations:
            fitness_class.reservations.remove(member.member_id)
            return {"status": "cancelled"}
        else:
            raise ValueError("Member not found in reservation list")