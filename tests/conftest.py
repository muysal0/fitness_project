import pytest
import os

# Pytest'e, uygulamanın 'src' klasöründe olduğunu bildiren bir yol ekleyelim.
# Bu, modül bulunamadı hatalarını önler.
@pytest.fixture(scope="session", autouse=True)
def set_pythonpath():
    """Testler başlamadan önce PYTHONPATH'e src dizinini ekler."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    src_path = os.path.join(project_root, 'src')
    
    if src_path not in os.environ.get('PYTHONPATH', '').split(os.pathsep):
        os.environ['PYTHONPATH'] = src_path + os.pathsep + os.environ.get('PYTHONPATH', '')
    
    # Flask uygulamasının direkt çalışmasını engellemek için main metodunu mocklayabiliriz
    # Ya da sadece `pytest --cov=src` komutunu `src` klasörünü hedef alarak çalıştırdığımızda
    # __name__ == "__main__" bloğu tetiklenmez zaten.

    # En temiz çözüm, app.py dosyasındaki __name__ == "__main__" bloğunu 
    # coverage'dan hariç tutan bir .coveragerc dosyası kullanmaktır.
    pass