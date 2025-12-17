class Member:
    def __init__(self, member_id, name, membership_type):
        """
        Üye sınıfı başlatıcı.
        :param member_id: Üyenin benzersiz numarası (int)
        :param name: Üyenin adı soyadı (str)
        :param membership_type: 'standard', 'premium' veya 'student' (str)
        """
        self.member_id = member_id
        self.name = name
        self.membership_type = membership_type