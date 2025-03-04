import requests
import logging
import subprocess
import sys
import time
import os

# Configurar logging con codificación UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def stop_ollama_service():
    try:
        logger.info("Deteniendo servicio Ollama existente...")
        subprocess.run(
            'taskkill /F /IM ollama.exe',
            shell=True,
            capture_output=True,
            text=True
        )
        time.sleep(2)  # Esperar a que el proceso termine
        return True
    except Exception as e:
        logger.error(f"Error deteniendo Ollama: {str(e)}")
        return False

def start_ollama_service():
    try:
        # Verificar si el puerto está en uso
        if check_port_in_use(11434):
            logger.warning("Puerto 11434 en uso. Deteniendo servicio existente...")
            if not stop_ollama_service():
                return False
        
        logger.info("Iniciando servicio Ollama...")
        process = subprocess.Popen(
            'ollama serve',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # Esperar a que el servicio esté disponible
        max_retries = 5
        while max_retries > 0:
            try:
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    logger.info("Servicio Ollama iniciado correctamente")
                    return True
            except:
                pass
            time.sleep(2)
            max_retries -= 1
            
        return False
    except Exception as e:
        logger.error(f"Error iniciando Ollama: {str(e)}")
        return False

def install_llama2():
    try:
        logger.info("Instalando modelo llama2...")
        # Configurar la codificación y el manejo de errores
        process = subprocess.Popen(
            'ollama pull llama2',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("Modelo llama2 instalado correctamente")
            return True
        else:
            logger.error(f"Error instalando llama2: {stderr}")
            return False
    except Exception as e:
        logger.error(f"Error ejecutando ollama pull: {str(e)}")
        return False

def verify_ollama():
    try:
        # Verificar el servicio
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            logger.error("Servicio Ollama no disponible. Intentando iniciar...")
            if not start_ollama_service():
                return False
            time.sleep(5)  # Esperar a que el servicio inicie
            
        # Verificar modelo
        models = response.json()
        logger.info(f"Modelos disponibles: {models}")
        
        if not models.get('models') or 'llama2' not in str(models):
            logger.warning("Modelo llama2 no encontrado. Intentando instalar...")
            if not install_llama2():
                return False
            time.sleep(10)  # Dar más tiempo para la instalación
        
        # Probar generación
        test_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama2",
                "prompt": "Hola mundo",
                "stream": False
            }
        )
        if test_response.status_code == 200:
            logger.info("Prueba de generación exitosa")
            logger.info(f"Respuesta: {test_response.json().get('response', '')}")
            return True
        else:
            logger.error(f"Error en prueba de generación: {test_response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if not verify_ollama():
        logger.error("\nVerificación fallida. Siga estos pasos manualmente:")
        print("\n1. Abra PowerShell como administrador y ejecute:")
        print("taskkill /F /IM ollama.exe")
        print("ollama serve")
        print("\n2. En otra terminal PowerShell, ejecute:")
        print("ollama pull llama2")
        print("ollama list")
        sys.exit(1)
    logger.info("Verificación completada exitosamente")
    sys.exit(0)