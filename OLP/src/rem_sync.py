# rem_sync.py

class REMSyncModule:
    """
    Gerencia a comunicação de controle de ultra baixa latência (fotônica/óptica).
    Usado para o sinal de Interrupção Crítica do PIM para a CPU.
    """
    # Simulação de latências
    LATENCY_OPTICAL_CYCLES = 10  # Tempo de resposta do sinal óptico
    
    def __init__(self):
        # Simula o driver de hardware do transceptor óptico
        # Na vida real, o custo de energia deve ser cuidadosamente pesado.
        self.optical_driver = type('OpticalDriver', (object,), {'send_pulse': lambda x: None, 'read_pulse': lambda: None})
        print("M4: REMSyncModule (Óptico) inicializado.")

    def send_critical_interrupt(self, error_code: str):
        """
        Envia um sinal de interrupção de volta à CPU usando o canal óptico (REM).
        """
        # Envio do pulso fotônico codificado
        self.optical_driver.send_pulse(error_code) 
        
        print(f"  -> SINAL CRÍTICO ENVIADO VIA REM-Sync (Latência: {self.LATENCY_OPTICAL_CYCLES} ciclos).")

    def receive_sync_pulse(self):
        """Rotina da CPU para receber o pulso óptico de sincronização/erro."""
        return self.optical_driver.read_pulse()