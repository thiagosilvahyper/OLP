# olp_hal_driver.py - Hardware Abstraction Layer (HAL) para OLP
# 280+ linhas de código robusto para comunicação com PIM/REM

import time
from typing import Dict, Optional, Tuple, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class HardwareRegister(Enum):
    """Mapeamento de registradores de hardware (Simulação)"""
    PIM_TASK_REGISTER = 0x80000000
    PIM_DATA_PTR_REGISTER = 0x80000004
    PIM_PREFETCH_DMA_CONFIG = 0x80000008
    PIM_STATUS_REGISTER = 0x8000000C
    REM_INTERRUPT_REGISTER = 0x90000000
    REM_STATUS_REGISTER = 0x90000004
    HW_TTID_COUNTER = 0xA0000000
    HW_ENERGY_MONITOR = 0xA0000004
    HW_ERROR_CODE = 0xA0000008
    HW_PERFORMANCE_METRICS = 0xA000000C


@dataclass
class HardwareEvent:
    """Registra um evento de hardware para auditoria"""
    timestamp: float
    event_type: str
    register: str
    value: int
    context: str = ""
    latency_ns: int = 0


@dataclass
class DMATransfer:
    """Informações sobre transferência DMA"""
    transfer_id: int
    source_addr: int
    dest_addr: int
    num_blocks: int
    timestamp_start: float = field(default_factory=time.time)
    timestamp_end: Optional[float] = None
    status: str = "PENDING"
    bytes_transferred: int = 0


class OLPHALDriver:
    """
    Hardware Abstraction Layer (OLP-HAL) para comunicação com hardware PIM/REM.
    
    Responsabilidades:
    1. Carregar tarefas no PIM via DMA (Direct Memory Access)
    2. Enviar sinais de interrupção crítica via REM (canal óptico)
    3. Monitorar latência (TTID) e consumo de energia em tempo real
    4. Registrar todos os eventos para auditoria completa
    5. Gerenciar fila de operações pendentes
    
    Rigor: Acesso direto aos registradores, sem overhead do SO
    Latência: Ultra-baixa (~8ns para REM, ~100ns para DMA)
    Auditoria: Log completo de todas as operações
    """
    
    def __init__(self, hal_version: str = "HAL-v1.0", cpu_freq_mhz: int = 3000):
        """
        Inicializar o driver HAL.
        
        Args:
            hal_version: Versão do driver
            cpu_freq_mhz: Frequência da CPU em MHz (padrão 3 GHz)
        """
        self.hal_version = hal_version
        self.cpu_frequency_mhz = cpu_freq_mhz
        
        # Registradores de hardware (simulação)
        self.registers: Dict[HardwareRegister, int] = {
            register: 0 for register in HardwareRegister
        }
        
        # Contadores e estatísticas
        self.pim_tasks_loaded = 0
        self.rem_interrupts_sent = 0
        self.dma_transfers_completed = 0
        self.total_bytes_transferred = 0
        self.total_energy_consumed_uj = 0
        
        # Histórico e fila de operações
        self.hw_events_log: List[HardwareEvent] = []
        self.dma_queue: Dict[int, DMATransfer] = {}
        self.next_transfer_id = 1
        
        # Métricas de performance
        self.metrics = {
            'avg_pim_latency_ns': 0,
            'max_pim_latency_ns': 0,
            'rem_latency_ns': 8,
            'total_pim_operations': 0,
            'total_rem_operations': 0
        }
        
        self.is_initialized = True
        
        logger.info(f"[OLP-HAL] {hal_version} inicializado com sucesso")
        logger.info(f"  - CPU Frequency: {cpu_freq_mhz} MHz")
        logger.info(f"  - Registradores: {len(HardwareRegister)}")
        logger.info(f"  - REM Latency: {self.metrics['rem_latency_ns']} ns")

    def write_register(self, register: HardwareRegister, value: int, 
                      context: str = "") -> bool:
        """
        Escrever valor em registrador de hardware.
        
        Args:
            register: Registrador alvo
            value: Valor a escrever
            context: Contexto da operação (para logging)
            
        Returns:
            True se bem-sucedido
        """
        try:
            start_time = time.perf_counter()
            
            self.registers[register] = value
            
            latency_ns = int((time.perf_counter() - start_time) * 1e9)
            
            self._log_event(
                event_type="REGISTER_WRITE",
                register=register.name,
                value=value,
                context=context,
                latency_ns=latency_ns
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[OLP-HAL] Erro ao escrever registrador: {e}")
            return False

    def read_register(self, register: HardwareRegister, 
                     context: str = "") -> int:
        """Ler valor de registrador de hardware"""
        try:
            start_time = time.perf_counter()
            
            value = self.registers.get(register, 0)
            
            latency_ns = int((time.perf_counter() - start_time) * 1e9)
            
            self._log_event(
                event_type="REGISTER_READ",
                register=register.name,
                value=value,
                context=context,
                latency_ns=latency_ns
            )
            
            return value
            
        except Exception as e:
            logger.error(f"[OLP-HAL] Erro ao ler registrador: {e}")
            return 0

    def load_task_pim(self, task_id: int, data_ptr: int, 
                     num_blocks: int, context: str = "") -> bool:
        """
        Carregar tarefa no PIM usando DMA (Direct Memory Access).
        
        Args:
            task_id: ID única da tarefa
            data_ptr: Ponteiro para os dados
            num_blocks: Número de blocos a transferir (64 bytes cada)
            context: Contexto (para logging)
            
        Returns:
            True se bem-sucedido
        """
        try:
            start_time = time.perf_counter()
            
            # 1. Configurar tarefa
            self.write_register(HardwareRegister.PIM_TASK_REGISTER, task_id, context)
            
            # 2. Configurar ponteiro de dados
            self.write_register(HardwareRegister.PIM_DATA_PTR_REGISTER, data_ptr, context)
            
            # 3. Configurar DMA
            block_size = 64
            total_bytes = num_blocks * block_size
            dma_config = (data_ptr & 0xFFFF0000) | (num_blocks & 0xFFFF)
            self.write_register(HardwareRegister.PIM_PREFETCH_DMA_CONFIG, 
                              dma_config, context)
            
            # 4. Simular latência de DMA (~100ns por bloco)
            simulated_dma_latency_ns = num_blocks * 100
            time.sleep(simulated_dma_latency_ns / 1e9)
            
            # 5. Disparar execução no PIM
            self.write_register(HardwareRegister.PIM_TASK_REGISTER, 1, context)
            
            # 6. Registrar transferência DMA
            dma_transfer = DMATransfer(
                transfer_id=self.next_transfer_id,
                source_addr=data_ptr,
                dest_addr=0x1000000,
                num_blocks=num_blocks,
                bytes_transferred=total_bytes,
                status="COMPLETED"
            )
            dma_transfer.timestamp_end = time.time()
            
            self.dma_queue[self.next_transfer_id] = dma_transfer
            self.next_transfer_id += 1
            
            # 7. Atualizar estatísticas
            self.pim_tasks_loaded += 1
            self.dma_transfers_completed += 1
            self.total_bytes_transferred += total_bytes
            self.metrics['total_pim_operations'] += 1
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            logger.debug(
                f"[OLP-HAL] Tarefa PIM carregada: task_id={task_id}, "
                f"blocks={num_blocks}, latency={latency_ms:.3f}ms"
            )
            
            self._log_event(
                event_type="PIM_TASK_LOADED",
                register="PIM_SYSTEM",
                value=task_id,
                context=context,
                latency_ns=int(latency_ms * 1e6)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[OLP-HAL] Erro ao carregar tarefa PIM: {e}")
            self.write_register(HardwareRegister.HW_ERROR_CODE, 0xFF, context)
            return False

    def send_rem_interrupt(self, error_code: int, 
                          context: str = "") -> bool:
        """
        Enviar sinal de interrupção crítica via REM (canal óptico).
        
        Args:
            error_code: Código de erro/falha a transmitir
            context: Contexto da falha
            
        Returns:
            True se bem-sucedido
        """
        try:
            start_time = time.perf_counter()
            
            # 1. Acesso direto ao registrador REM
            self.write_register(HardwareRegister.REM_INTERRUPT_REGISTER, 
                              error_code, context)
            
            # 2. Latência do sinal REM (ultra-baixa: ~8ns)
            rem_latency_ns = 8
            time.sleep(rem_latency_ns / 1e9)
            
            # 3. Registrar status
            self.write_register(HardwareRegister.REM_STATUS_REGISTER, 
                              0x01, context)
            
            # 4. Atualizar estatísticas
            self.rem_interrupts_sent += 1
            self.metrics['total_rem_operations'] += 1
            
            total_latency_ns = int((time.perf_counter() - start_time) * 1e9)
            
            logger.debug(
                f"[OLP-HAL] REM Interrupt enviado: error_code={hex(error_code)}, "
                f"latency={total_latency_ns}ns"
            )
            
            self._log_event(
                event_type="REM_INTERRUPT_SENT",
                register="REM_CONTROL",
                value=error_code,
                context=context,
                latency_ns=total_latency_ns
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[OLP-HAL] Erro ao enviar REM interrupt: {e}")
            return False

    def get_current_ttid(self) -> float:
        """
        Obter TTID (Tempo-para-Conclusão da Inferência) atual em milissegundos.
        
        Returns:
            TTID em milissegundos (float)
        """
        try:
            cycle_count = self.read_register(HardwareRegister.HW_TTID_COUNTER)
            ttid_ms = (cycle_count / (self.cpu_frequency_mhz * 1e6)) * 1000
            return max(0.0, ttid_ms)
            
        except Exception as e:
            logger.error(f"[OLP-HAL] Erro ao obter TTID: {e}")
            return 0.0

    def get_energy_consumption(self) -> float:
        """
        Obter consumo de energia atual em Watts.
        
        Returns:
            Potência em Watts (float)
        """
        try:
            energy_value = self.read_register(HardwareRegister.HW_ENERGY_MONITOR)
            power_watts = (energy_value / 1000.0)
            return max(0.0, power_watts)
            
        except Exception as e:
            logger.error(f"[OLP-HAL] Erro ao obter consumo: {e}")
            return 0.0

    def get_hardware_stats(self) -> Dict:
        """Retornar estatísticas completas de hardware"""
        
        avg_pim_latency = 0
        if self.dma_transfers_completed > 0:
            total_latency = sum(
                (t.timestamp_end - t.timestamp_start) * 1e9
                for t in self.dma_queue.values()
                if t.timestamp_end is not None
            )
            avg_pim_latency = int(total_latency / self.dma_transfers_completed)
        
        return {
            'driver_version': self.hal_version,
            'is_initialized': self.is_initialized,
            'pim_tasks_loaded': self.pim_tasks_loaded,
            'rem_interrupts_sent': self.rem_interrupts_sent,
            'dma_transfers_completed': self.dma_transfers_completed,
            'total_bytes_transferred': self.total_bytes_transferred,
            'current_ttid_ms': self.get_current_ttid(),
            'current_power_w': self.get_energy_consumption(),
            'avg_pim_latency_ns': avg_pim_latency,
            'rem_latency_ns': self.metrics['rem_latency_ns'],
            'total_hw_events': len(self.hw_events_log),
            'pending_dma_transfers': len([t for t in self.dma_queue.values() 
                                         if t.status == "PENDING"]),
            'metrics': self.metrics
        }

    def get_dma_status(self, transfer_id: Optional[int] = None) -> Dict:
        """Obter status de transferências DMA"""
        if transfer_id is not None:
            if transfer_id in self.dma_queue:
                t = self.dma_queue[transfer_id]
                return {
                    'transfer_id': t.transfer_id,
                    'status': t.status,
                    'bytes': t.bytes_transferred,
                    'duration_ms': (t.timestamp_end - t.timestamp_start) * 1000 
                                  if t.timestamp_end else 0
                }
            return {}
        
        return {
            'total_transfers': len(self.dma_queue),
            'completed': sum(1 for t in self.dma_queue.values() if t.status == "COMPLETED"),
            'pending': sum(1 for t in self.dma_queue.values() if t.status == "PENDING"),
            'transfers': {
                tid: {
                    'status': t.status,
                    'bytes': t.bytes_transferred,
                    'duration_ms': (t.timestamp_end - t.timestamp_start) * 1000
                              if t.timestamp_end else 0
                }
                for tid, t in self.dma_queue.items()
            }
        }

    def _log_event(self, event_type: str, register: str, value: int,
                  context: str = "", latency_ns: int = 0) -> None:
        """Registrar evento de hardware para auditoria"""
        
        event = HardwareEvent(
            timestamp=time.time(),
            event_type=event_type,
            register=register,
            value=value,
            context=context,
            latency_ns=latency_ns
        )
        
        self.hw_events_log.append(event)
        
        if len(self.hw_events_log) > 10000:
            self.hw_events_log = self.hw_events_log[-5000:]

    def get_event_log(self, limit: int = 20, 
                     event_type_filter: Optional[str] = None) -> List[Dict]:
        """Retornar últimos N eventos de hardware"""
        events = self.hw_events_log
        
        if event_type_filter:
            events = [e for e in events if e.event_type == event_type_filter]
        
        selected = events[-limit:] if limit > 0 else events
        
        return [
            {
                'timestamp': e.timestamp,
                'event_type': e.event_type,
                'register': e.register,
                'value': hex(e.value) if e.value > 0 else '0x0',
                'context': e.context,
                'latency_ns': e.latency_ns
            }
            for e in selected
        ]

    def export_hal_diagnostics(self, filepath: str = "hal_diagnostics.json") -> bool:
        """Exportar diagnósticos do HAL para análise"""
        try:
            diagnostics = {
                'timestamp': datetime.now().isoformat(),
                'driver_version': self.hal_version,
                'statistics': self.get_hardware_stats(),
                'dma_status': self.get_dma_status(),
                'recent_events': self.get_event_log(limit=100),
                'performance_metrics': self.metrics
            }
            
            with open(filepath, 'w') as f:
                json.dump(diagnostics, f, indent=2, default=str)
            
            logger.info(f"[OLP-HAL] Diagnósticos exportados para {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"[OLP-HAL] Erro ao exportar diagnósticos: {e}")
            return False


# Instância global do driver
OLP_HAL = OLPHALDriver(hal_version="HAL-v1.0-Conceitual", cpu_freq_mhz=3000)