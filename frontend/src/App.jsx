import { useState } from 'react'

function App() {
  // 1. A nossa "memória" para o formulário
  const [viagem, setViagem] = useState({
    origin: '',
    destination: '',
    start_date: '',
    end_date: ''
  })

  // 2. A função que atualiza a memória sempre que escrevemos algo
  const handleChange = (e) => {
    const { name, value } = e.target
    setViagem(prev => ({ ...prev, [name]: value }))
  }

  const pesquisarViagem = () => {
    // Para já, vamos apenas imprimir os dados para confirmar que estão corretos
    console.log("Dados prontos a enviar para o Backend:", viagem);
  }

  // 3. A interface (O teu desafio começa aqui!)
  return (
    <div>
      <h1>Smart Trip Planner</h1>
        <input type="text" name="origin" value={viagem.origin} onChange={handleChange} />
        <input type="text" name="destination" value={viagem.destination} onChange={handleChange} />
        <input type="date" name="start_date" value={viagem.start_date} onChange={handleChange} />
        <input type="date" name="end_date" value={viagem.end_date} onChange={handleChange} />

        <button onClick={pesquisarViagem}>Procurar Viagem</button>

    </div>
  )
}

export default App