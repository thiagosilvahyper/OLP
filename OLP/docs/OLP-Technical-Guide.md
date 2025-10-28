# OLP (Otimizador de Localidade Preditivo) - Guia Técnico Completo

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Componentes Principais](#componentes-principais)
4. [Fluxo de Execução](#fluxo-de-execução)
5. [Decisão OLP-ALP](#decisão-olp-alp)
6. [Integração e Uso](#integração-e-uso)
7. [Exemplos Práticos](#exemplos-práticos)
8. [Próximos Passos](#próximos-passos)

---

## Visão Geral

O **OLP (Otimizador de Localidade Preditivo)** é um sistema híbrido de hardware-software que otimiza a execução de tarefas sensíveis à latência (IA, Big Data, HPC) decidindo dinamicamente se devem ser executadas em:

- **PIM (Processing-in-Memory)**: Hardware especializado, ultra-rápido, com latência baixa
- **CPU**: Processador geral, com maior flexibilidade

### Objetivos Principais

| Objetivo | Descrição | Métrica |
|----------|-----------|---------|
| **Rigor** | Decisões baseadas em confiança >= 99.9% | Confiança do ML |
| **Ganho** | Otimização de latência (TTID) | TTID_CPU - TTID_PIM |
| **Segurança** | Recovery automático em caso de falhas críticas | Taxa de sucesso 100% |
| **Latência** | Interface de baixa latência para aplicações | <1ms overhead |

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    APLICAÇÃO DO DESENVOLVEDOR                   │
│        (Machine Learning, Big Data, High-Performance)           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────────┐
        │         OLP Core API (Interface)             │
        │   ✓ set_context()                           │
        │   ✓ execute_optimized()                     │
        │   ✓ register_checkpoint()                   │
        └──────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┬──────────────┐
        ▼                              ▼              ▼
    ┌────────┐                    ┌──────────┐   ┌────────────┐
    │ Tracer │                    │ML_Model  │   │ Recovery   │
    │(M1)    │                    │ALP(M2)   │   │Module(M3)  │
    ├────────┤                    ├──────────┤   ├────────────┤
    │• Collect│                    │• Predict │   │• Checkpoint│
    │ accesses│                    │ blocks   │   │• Rollback  │
    │• Stride │                    │• Confidence   │• Recovery  │
    │ pattern │                    │• TTID est.    │ via REM    │
    │• Context│                    │              │            │
    └───┬────┘                    └──────┬──────┘ └────┬───────┘
        │                                │            │
        └────────────────┬────────────────┴────────────┘
                         ▼
        ┌──────────────────────────────────────┐
        │  PredictionEngine (Motor de Decisão) │
        │      Lógica OLP-ALP                  │
        ├──────────────────────────────────────┤
        │ IF confiança >= 99.9% AND ganho > 0:│
        │    → Desvia para PIM                 │
        │ ELSE:                                │
        │    → Executa na CPU                  │
        └────────────────┬─────────────────────┘
                         ▼
        ┌──────────────────────────────────────┐
        │   OLP-HAL Driver (Camada HW)         │
        │   Hardware Abstraction Layer         │
        ├──────────────────────────────────────┤
        │ • load_task_pim() [DMA]              │
        │ • send_rem_interrupt() [REM]         │
        │ • Monitor (TTID, Power)              │
        └────────┬───────────────┬────┬────────┘
                 ▼               ▼    ▼
            ┌──────────┐    ┌────────┐  ┌────────────┐
            │ PIM Unit │    │REM(Opt)│  │ HW Monitor │
            │(Hardware)│    │Signal  │  │(TTID, W)   │
            └──────────┘    └────────┘  └────────────┘
```

---

## Componentes Principais

### 1. **OLPCoreAPI** - Interface Principal

**Arquivo**: `olp_core_api.py`

Interface que o desenvolvedor interage diretamente. Coordena todos os módulos internos.

#### Métodos Essenciais:

```python
# 1. Definir Contexto (Obrigatório)
OLP_API.set_context(
    function_name: str,      # Ex: "training_loop_forward_pass"
    scope_id: int,           # Ex: número da iteração (1, 2, 3...)
    metadata: Dict = None    # Informações adicionais opcionais
) -> bool

# 2. Executar Tarefa Otimizada (Principal)
result = OLP_API.execute_optimized(
    task_function: Callable,  # Função a ser executada
    task_data: List,          # Dados / endereços de memória
    task_id: int = None       # ID opcional da tarefa
) -> Any

# 3. Registrar Checkpoint (Segurança)
OLP_API.register_checkpoint(
    recovery_address: int,     # Endereço de estado válido
    checkpoint_name: str = ""  # Nome descritivo
) -> bool

# 4. Ativar Recovery (Emergência)
OLP_API.trigger_recovery(
    error_code: int,           # Código de erro
    context_info: str = ""     # Contexto da falha
) -> bool

# 5. Obter Relatório Completo
report = OLP_API.get_full_system_report() -> Dict
```

#### Responsabilidades:
- Coordenar Tracer, ML_Model, PredictionEngine, Recovery
- Manter stack de contextos
- Rastrear histórico de execuções
- Fornecer estatísticas e relatórios

---

### 2. **RuntimeTracer (M1)** - Coleta de Dados

**Arquivo**: `runtime_tracer.py`

Coleta padrões de acesso à memória em tempo de execução.

#### Responsabilidades:
- Registrar o **contexto da aplicação** (função, escopo)
- Logar **acessos à memória** (endereços, tipos)
- Calcular **sequências de stride** (diferenças entre acessos)
- Fornecer feedback para ML_Model

#### Métodos:
```python
tracer.set_context(function_name: str, scope_id: int)
tracer.log_access(address: int, access_type: str = "READ")
tracer.get_stride_pattern(context_key: str) -> List[int]
tracer.get_timestamp() -> float
tracer.get_tracer_stats() -> Dict
```

#### Exemplo de Uso:
```python
tracer.set_context("matrix_multiply", 5)
tracer.log_access(0x1000)  # Lê endereço
tracer.log_access(0x1008)  # Próximo acesso
tracer.log_access(0x1010)  # Stride = 8 bytes

strides = tracer.get_stride_pattern()  # [8, 8] → Padrão regular!
```

---

### 3. **ALPModel (M2)** - Modelo de ML

**Arquivo**: `alp_model.py`

Modelo de Previsão de Localidade Adaptativa baseado em LSTM conceitual.

#### Responsabilidades:
- **Preprocessar** sequências de stride (normalização, padronização)
- **Executar inferência** para prever próximos blocos
- **Calcular confiança** da previsão (rigor >= 99.9%)
- **Manter histórico** de padrões por contexto

#### Método Principal:
```python
prediction = model.predict(
    context: str,        # Ex: "matrix_multiply_5"
    accesses: List[int]  # Histórico de endereços
) -> Dict

# Retorna:
{
    'blocks': [0x1008, 0x1010, 0x1018],  # Blocos a prefetch
    'confidence': 0.99999,                # 99.999% de confiança
    'ttid_pim': 95,                       # Tempo estimado PIM (ms)
    'ttid_cpu': 160,                      # Tempo estimado CPU (ms)
    'stride_pattern': 'Regular (mean=8, std=0.5)'
}
```

#### Lógica de Rigor:

| Contexto | Padrão | Confiança | Blocos | Ação |
|----------|--------|-----------|--------|------|
| `matrix_multiply` + stride regular | Linear | 99.999% | ✓ Prever | PIM |
| Loop genérico + padrão moderado | Moderado | 99.5% | ✓ Prever | Decisão |
| Contexto novo / padrão caótico | Desconhecido | 75% | ✗ Vazio | CPU |

---

### 4. **PredictionEngine (M2)** - Motor de Decisão

**Arquivo**: `prediction_engine.py`

Toma a decisão final: **PIM** ou **CPU**.

#### Algoritmo OLP-ALP:

```python
def decide(confidence, ttid_pim, ttid_cpu):
    ttid_gain = ttid_cpu - ttid_pim
    
    if confidence >= 0.999 and ttid_gain > 0:
        return "PIM"      # Confiança alta + ganho positivo
    else:
        return "CPU"      # Fallback seguro
```

#### Método:
```python
decision = engine.execute_task(
    task_function,
    task_data,
    tracer,
    ml_model,
    hal_driver
) -> Dict

# Retorna:
{
    'destination': 'PIM',           # PIM ou CPU
    'confidence': 0.99999,
    'ttid': 95.2,                   # Tempo real de execução (ms)
    'ttid_estimate': 95,            # Tempo estimado
    'result': <resultado da tarefa>,
    'gain': 65                       # ttid_cpu - ttid_pim
}
```

---

### 5. **OLP-HAL Driver** - Abstração de Hardware

**Arquivo**: `olp_hal_driver.py`

Comunicação de baixa latência com PIM/REM.

#### Interfaces Principais:

```python
# 1. Carregar Tarefa no PIM via DMA
hal_driver.load_task_pim(
    task_id: int,      # ID da tarefa
    data_ptr: int,     # Ponteiro para dados
    num_blocks: int    # Número de blocos
) -> bool

# 2. Enviar Sinal de Interrupção Crítica via REM
hal_driver.send_rem_interrupt(
    error_code: int,
    context: str = ""
) -> bool

# 3. Monitorar TTID em Tempo Real
ttid_ms = hal_driver.get_current_ttid() -> float

# 4. Obter Relatório de Hardware
stats = hal_driver.get_hardware_stats() -> Dict
```

#### Registradores de Hardware (Simulados):

| Registrador | Endereço | Função |
|-------------|----------|--------|
| `PIM_TASK_REGISTER` | 0x80000000 | Controlar tarefa PIM |
| `PIM_DATA_PTR_REGISTER` | 0x80000004 | Dados a transferir |
| `PIM_PREFETCH_DMA_CONFIG` | 0x80000008 | Configurar DMA |
| `REM_INTERRUPT_REGISTER` | 0x90000000 | Pulso óptico (REM) |
| `HW_TTID_COUNTER` | 0xA0000000 | Contador de latência |
| `HW_ENERGY_MONITOR` | 0xA0000004 | Consumo de energia |

#### Características de Rigor:
- **Acesso Direto**: Bypasssa overhead do SO
- **DMA**: Transferência direta de dados (ultra-rápido)
- **Ultra-Baixa Latência**: ~8ns para REM
- **Auditoria Completa**: Log de todos os eventos

---

### 6. **PIMRecoveryModule (M3)** - Recuperação de Falhas

**Arquivo**: `pim_recovery.py`

Detecta e recupera de falhas críticas no PIM.

#### Responsabilidades:
- Manter **checkpoints** de estado válido
- Monitorar **sinais de falha** (REM)
- Fazer **rollback** para checkpoint seguro
- Reexecutar na **CPU** como fallback

#### Métodos:

```python
# 1. Registrar Checkpoint
recovery.register_checkpoint(
    address: int,              # Endereço de estado válido
    checkpoint_name: str = ""
) -> None

# 2. Tratar Falha Crítica
recovery.handle_critical_interrupt(
    error_code: int,
    context: str
) -> None

# 3. Obter Estatísticas
stats = recovery.get_recovery_stats() -> Dict
```

#### Fases de Recuperação:

```
1. DETECÇÃO: Hardware PIM reporta erro via REM
   ↓
2. LOG: Registrar erro e contexto
   ↓
3. ROLLBACK: Retornar ao último checkpoint válido
   ↓
4. CPU_FALLBACK: Reexecutar a tarefa na CPU
   ↓
5. VALIDAÇÃO: Garantir resultado correto ao usuário
```

---

## Fluxo de Execução

### Passo a Passo Detalhado

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. DESENVOLVEDOR DEFINE CONTEXTO                               │
└─────────────────────────────────────────────────────────────────┘

olp_api.set_context("training_loop_forward_pass", iteration=5)

Resultado:
  - RuntimeTracer inicia rastreamento para este contexto
  - Pilha de contextos atualizada
  - ID único gerado: "training_loop_forward_pass_5"

┌─────────────────────────────────────────────────────────────────┐
│ 2. DESENVOLVEDOR REGISTRA CHECKPOINT                           │
└─────────────────────────────────────────────────────────────────┘

olp_api.register_checkpoint(0x500 + 5*8, "batch_5_start")

Resultado:
  - PIMRecoveryModule armazena checkpoint
  - Endereço marcado como "último bom estado"
  - ID único gerado: "batch_5_start"

┌─────────────────────────────────────────────────────────────────┐
│ 3. DESENVOLVEDOR EXECUTA TAREFA OTIMIZADA                      │
└─────────────────────────────────────────────────────────────────┘

result = olp_api.execute_optimized(matrix_multiply, data_addresses)

Resultado interno (detalhado):

  [Fase 1: Coleta de Dados]
    RuntimeTracer.log_access(0x1000)  # Coleta todos os acessos
    RuntimeTracer.log_access(0x1008)  # durante a execução
    RuntimeTracer.log_access(0x1010)  # da tarefa
    
    Stride detectado: [8, 8] → Padrão MUITO regular!
  
  [Fase 2: Previsão via ML]
    ALPModel.preprocess_input("training_loop_forward_pass_5", accesses)
    
    Input: [0x1000, 0x1008, 0x1010] (endereços históricos)
    Output: [0x1018, 0x1020, 0x1028] (próximos blocos preditos)
    
    Predict():
      - Contexto: "training_loop_forward_pass"
      - Padrão: LSTM detecta "loop matrix_multiply"
      - Confiança: 99.999% (stride muito regular)
      - TTID estimado PIM: 95 ms
      - TTID estimado CPU: 160 ms
  
  [Fase 3: Decisão OLP-ALP]
    PredictionEngine:
      - Confiança 99.999% >= 99.9%? ✓ SIM
      - Ganho = 160 - 95 = 65 ms > 0? ✓ SIM
      - Decisão: DESVIA PARA PIM
  
  [Fase 4: Execução no PIM]
    OLPHALDriver.load_task_pim(
      task_id=12345,
      data_ptr=0x1000,
      num_blocks=3
    )
    
    Hardware:
      1. DMA transfere blocos [0x1018, 0x1020, 0x1028] para cache PIM
      2. PIM Unit executa matrix_multiply em paralelo
      3. Resultado pronto em ~95 ms (real TTID)
  
  [Fase 5: Retorno ao Aplicativo]
    OLP_API retorna resultado
    Log registrado: "Task #1 -> PIM (confiança: 99.999%)"
```

---

## Decisão OLP-ALP

### Lógica de Rigor

```python
def olp_alp_decision(confidence, ttid_pim, ttid_cpu):
    """
    Algoritmo de decisão com dois critérios de rigor:
    1. Confiança >= 99.9% (C >= 0.999)
    2. Ganho positivo (TTID_gain > 0)
    """
    
    ttid_gain = ttid_cpu - ttid_pim
    
    # Critério 1: Confiança Suficiente
    if confidence < 0.999:
        print("❌ Confiança insuficiente: usar CPU")
        return "CPU"
    
    # Critério 2: Ganho Positivo
    if ttid_gain <= 0:
        print("❌ Sem ganho de latência: usar CPU")
        return "CPU"
    
    # Ambos critérios satisfeitos
    print(f"✓ DESVIAR PARA PIM")
    print(f"  - Confiança: {confidence*100:.3f}%")
    print(f"  - Ganho TTID: {ttid_gain} ms")
    return "PIM"
```

### Tabela de Decisões

| Confiança | Ganho TTID | Decisão | Justificativa |
|-----------|-----------|---------|---------------|
| 99.999% | +65 ms | **PIM** | Ambos critérios ok |
| 99.5% | +50 ms | **CPU** | Confiança baixa demais |
| 99.999% | -10 ms | **CPU** | Sem ganho de latência |
| 95% | +100 ms | **CPU** | Confiança crítica |
| 99.9% | +1 ms | **PIM** | Marginal, mas ok |

---

## Integração e Uso

### Passo 1: Instalar Dependências

```bash
# Nenhuma dependência externa é estritamente necessária
# Usa apenas stdlib do Python
```

### Passo 2: Importar OLP

```python
from olp_core_api import OLP_API
```

### Passo 3: Usar a API (3 Operações)

```python
# 1. Definir contexto
OLP_API.set_context("training_loop", iteration=1)

# 2. Registrar checkpoint de segurança
OLP_API.register_checkpoint(0x500, "checkpoint_1")

# 3. Executar com otimização
def minha_tarefa(dados):
    return sum(dados) * 2

dados_enderecos = [0x1000 + i*8 for i in range(10)]
resultado = OLP_API.execute_optimized(minha_tarefa, dados_enderecos)

# 4. Obter relatório
relatorio = OLP_API.get_full_system_report()
print(relatorio)
```

---

## Exemplos Práticos

### Exemplo 1: Loop de Treinamento ML

```python
from olp_core_api import OLP_API

def forward_pass(batch_data):
    """Passe forward de uma rede neural."""
    result = 0
    for x in batch_data:
        result += x ** 2
    return result

# Loop de treinamento com OLP
for epoch in range(1, 11):
    for batch in range(1, 51):
        # 1. Define contexto específico
        OLP_API.set_context("training_forward_pass", epoch * 100 + batch)
        
        # 2. Checkpoint para segurança
        checkpoint_addr = 0x1000 + (epoch * 50 + batch) * 8
        OLP_API.register_checkpoint(checkpoint_addr, f"epoch_{epoch}_batch_{batch}")
        
        # 3. Simular dados de entrada (endereços de memória)
        batch_data = [0x2000 + i*8 for i in range(batch * 10)]
        
        # 4. Executar com OLP decidindo PIM vs CPU
        loss = OLP_API.execute_optimized(forward_pass, batch_data)
        
        if batch % 10 == 0:
            print(f"Epoch {epoch}, Batch {batch}: Loss = {loss}")
```

### Exemplo 2: Big Data Processing

```python
def aggregate_data(addresses):
    """Agregar dados com padrão de acesso previsível."""
    total = sum(addresses)
    return total // len(addresses)

# Processamento de dados com OLP
for chunk_id in range(1, 100):
    # Define contexto de processamento
    OLP_API.set_context("big_data_aggregation", chunk_id)
    OLP_API.register_checkpoint(0x5000 + chunk_id * 8, f"chunk_{chunk_id}")
    
    # Endereços de dados (em padrão linear)
    chunk_addresses = [0x10000 + i*64 for i in range(1000)]
    
    # OLP decide automaticamente
    result = OLP_API.execute_optimized(aggregate_data, chunk_addresses)
```

---

## Próximos Passos

### Curto Prazo (1-2 semanas)
1. ✅ Implementar suite de testes (unit + integration)
2. ✅ Otimizar latência do OLP-HAL Driver
3. ✅ Implementar cache de previsões para contextos repetidos
4. ✅ Documentação de API (Sphinx)

### Médio Prazo (1-2 meses)
1. Integração com LSTM weights reais (treinar com datasets reais)
2. Dashboard de monitoring em tempo real
3. Perfil de performance (micro-benchmarks)
4. Suporte a múltiplas arquiteturas de PIM

### Longo Prazo (3-6 meses)
1. Hardware real: implementar driver para PIM físico
2. Otimizações adaptativas (ajustar threshold de confiança)
3. Suporte a múltiplos contextos concorrentes
4. Publicação de resultados (papers, conferences)

---

## Referências Técnicas

### Documentação de Componentes
- `alp_model.py`: Modelo de ML com LSTM conceitual
- `olp_hal_driver.py`: Driver de comunicação com hardware
- `olp_core_api.py`: Interface principal para desenvolvedores
- `runtime_tracer.py`: Coleta de padrões de acesso
- `prediction_engine.py`: Motor de decisão OLP-ALP
- `pim_recovery.py`: Módulo de recuperação de falhas

### Princípios de Design
- **Simplicidade**: 3 chamadas de API para o desenvolvedor
- **Rigor**: Confiança >= 99.9% para decisões críticas
- **Segurança**: Recovery automático em caso de falhas
- **Latência**: Ultra-baixa (<1ms overhead)

---

**Fim do Guia Técnico**
