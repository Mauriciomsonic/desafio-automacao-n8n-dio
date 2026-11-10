"""
=============================================================================
Notificador de Áudio & Efeitos Sonoros do Ciclo de Execução
Projeto: Automação Caçador de Vagas ATS (DIO Santander / N8N)
=============================================================================
Funcionalidades:
1. Emissão de efeito sonoro harmônico e não invasivo a cada ciclo concluído.
2. Garantia de execução idempotente (exatamente uma vez por ciclo de execução).
3. Operação 100% assíncrona (não adiciona latência ao pipeline).
4. Tolerância total a falhas (opera normalmente caso o sistema não possua placa de som).
=============================================================================
"""

import os
import sys
import math
import wave
import struct
import threading
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOM_WAV_PATH = os.path.join(ASSETS_DIR, "som_ciclo_concluido.wav")

# Controle de estado para garantir disparo estritamente único por ciclo
_runs_notificados = set()
_lock = threading.Lock()

def _garantir_arquivo_audio_wav():
    """Gera um arquivo de áudio WAV harmônico suave caso ainda não exista."""
    if os.path.exists(SOM_WAV_PATH):
        return

    os.makedirs(ASSETS_DIR, exist_ok=True)
    sample_rate = 44100
    duracao_total = 0.40  # 400 milissegundos
    n_samples = int(sample_rate * duracao_total)
    
    # Sintetiza dois tons harmônicos sucessivos: 587.33 Hz (D5) -> 880.00 Hz (A5)
    frequencias = [587.33, 880.00]
    mid = n_samples // 2

    with wave.open(SOM_WAV_PATH, "w") as wav_file:
        wav_file.setnchannels(1)      # Mono
        wav_file.setsampwidth(2)      # 16-bit
        wav_file.setframerate(sample_rate)

        frames = bytearray()
        for i in range(n_samples):
            # Transição suave entre a primeira e a segunda nota
            freq = frequencias[0] if i < mid else frequencias[1]
            t = i / sample_rate
            
            # Envelope exponencial suave para evitar estalo no áudio
            decay = math.exp(-3.5 * (t / duracao_total))
            amplitude = 0.28 * decay
            
            valor = int(32767.0 * amplitude * math.sin(2.0 * math.pi * freq * t))
            frames.extend(struct.pack("<h", max(-32768, min(32767, valor))))

        wav_file.writeframes(frames)

def tocar_efeito_sonoro_ciclo(run_id: Optional[str] = None, forcar: bool = False) -> bool:
    """
    Dispara o efeito sonoro de conclusão do ciclo exatamente uma vez.
    Retorna True se o som foi emitido, ou False se já havia sido emitido para este ciclo.
    """
    global _runs_notificados

    chave_execucao = run_id or "ciclo_atual"
    
    with _lock:
        if not forcar and chave_execucao in _runs_notificados:
            # Proteção contra repetições de estado ou renderizações
            return False
        _runs_notificados.add(chave_execucao)

    def _reproduzir_audio():
        try:
            _garantir_arquivo_audio_wav()
            
            # Reprodução nativa no Windows sem dependências externas
            if sys.platform.startswith("win"):
                import winsound
                # SND_ASYNC garante que a chamada retorne instantaneamente
                flags = winsound.SND_FILENAME | winsound.SND_ASYNC
                winsound.PlaySound(SOM_WAV_PATH, flags)
            else:
                # Fallback multiplataforma (Linux / macOS)
                if sys.platform == "darwin":
                    os.system(f"afplay '{SOM_WAV_PATH}' &")
                else:
                    os.system(f"aplay -q '{SOM_WAV_PATH}' & 2>/dev/null")
        except Exception:
            # Em ambientes sem áudio ou silenciosos, nunca quebra o ciclo
            pass

    # Executa em thread separada para não bloquear absolutamente nada
    t = threading.Thread(target=_reproduzir_audio, daemon=True)
    t.start()
    return True

def resetar_controle_som(run_id: Optional[str] = None):
    """Permite resetar o controle de áudio antes de um novo ciclo de agendamento."""
    global _runs_notificados
    with _lock:
        if run_id:
            _runs_notificados.discard(run_id)
        else:
            _runs_notificados.clear()

if __name__ == "__main__":
    print("Testando emissão de efeito sonoro do ciclo...")
    tocar_efeito_sonoro_ciclo(run_id="teste_manual", forcar=True)
    import time
    time.sleep(0.5)
    print("Teste de som finalizado com sucesso!")
