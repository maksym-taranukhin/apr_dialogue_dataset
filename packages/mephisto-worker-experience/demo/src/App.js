import React from "react";
import "./index.css";
import { Tips, createTip } from "mephisto-worker-experience";

function App() {
  return (
    <div className="container">
      <Tips
        handleSubmit={(tipData) =>
          console.log(createTip(tipData.header, tipData.text))
        }
        maxHeight="25rem"
        maxWidth="25rem"
        placement="right-start"
        list={[
          {
            header: "Functional or Class Components?",
            text:
              "It is generally advised to use functional components as they are thought to be the future of React.",
          },
          {
            header: "When to Use Context?",
            text:
              "To avoid having to pass props down 3+ levels, the createContext() and useContext() methods can be used.",
          },
        ]}
      />
    </div>
  );
}

export default App;
