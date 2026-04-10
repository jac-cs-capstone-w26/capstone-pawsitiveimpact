import React from "react";
import ActuatorToggle from "../components/ActuatorToggle";
import SensorGraph from "../components/SensorGraph";

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
      
      {/* Title */}
      <h1 className="text-3xl font-bold mb-6 text-gray-800">
         Device Dashboard
      </h1>

      {/* Actuators Card */}
      <div className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-xl mb-8">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">
          Actuators
        </h2>

        <div className="flex justify-around">
          <ActuatorToggle id="led" />
          <ActuatorToggle id="fan" />
        </div>
      </div>

      {/* Sensors Card */}
      <div className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-3xl">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">
          Sensor Readings
        </h2>

        <SensorGraph />
      </div>
    </div>
  );
};

export default App;