import React, { useState } from "react";

interface Props {
  id: string; // "led" or "fan"
}

const ActuatorToggle: React.FC<Props> = ({ id }) => {
  const [state, setState] = useState(false); // false = off, true = on

  const toggle = async () => {
    const newState = !state;
    try {
      await fetch(`http://172.20.10.2:8000/control/${id}?state=${newState ? "on" : "off"}`, {
        method: "PUT",
      });
      setState(newState);
    } catch (err) {
      console.error("Error toggling actuator:", err);
    }
  };

return (
  <button
    onClick={toggle}
    className={`
      px-6 py-3 rounded-xl font-semibold text-white transition-all duration-300
      shadow-md hover:scale-105 active:scale-95
      ${state ? "bg-green-500 hover:bg-green-600" : "bg-red-500 hover:bg-red-600"}
    `}
  >
    {id.toUpperCase()}
    <div className="text-sm opacity-80">
      {state ? "ON" : "OFF"}
    </div>
  </button>
);
};

export default ActuatorToggle;