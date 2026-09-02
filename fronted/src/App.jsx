import { useState } from 'react'
import './App.css'

function App() {
  const [dutyList, setDutyList] = useState([
    {
      name: "אבי שוחמכר",
      phoneNumber: "03993",
    }
  ])

  const [currentDuty, setCurrentDuty] = useState(0)

  const currentPerson = dutyList[currentDuty]

  const callDuty = () => {
    window.location.href = `tel:${currentPerson.phoneNumber}`
  }

  return (
    <main className="app">
      <div className="duty-container">

        <p className="subtitle">
          התורן השבוע
        </p>

        <div className="duty-circle">
          <span>{currentPerson.name}</span>
        </div>

        <button className="phone-button" onClick={callDuty}>
          <span className="phone-icon">☎</span>
        </button>

      </div>
    </main>
  )
}

export default App
