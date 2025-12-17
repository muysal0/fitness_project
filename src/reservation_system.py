class ReservationManager:
    def book_class(self, member, fitness_class):
        """
        Üyeyi derse kaydeder.
        """
        # 1. Kapasite Kontrolü
        if fitness_class.current_occupancy() >= fitness_class.capacity:
            raise ValueError("Class is full")

        # --- YENİ EKLENEN KISIM: Çifte Kayıt Kontrolü ---
        if member.member_id in fitness_class.reservations:
            raise ValueError("Member already booked this class")
        # -----------------------------------------------

        # 2. Rezervasyon İşlemi
        fitness_class.reservations.append(member.member_id)

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