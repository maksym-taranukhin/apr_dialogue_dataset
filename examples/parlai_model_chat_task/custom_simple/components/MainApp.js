/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { ChatApp, INPUT_MODE, AppContext } from "bootstrap-chat";
import RenderChatMessage from "./RenderChatMessage";
import CustomTextResponse from "./CustomTextResponse";
import StatementList from "./StatementList";



function MainApp() {
  const [messages, setMessages] = React.useState([]);
  const [documents, setDocuments] = React.useState([]);

  return (
    <ChatApp


      onMessagesChange={(newMessages) => {
        console.log("Messages: ", newMessages);

        // Spread into a new array
        setMessages([...newMessages]);
        // Save documents from the last message
        setDocuments(newMessages[newMessages.length - 1]?.task_data?.retrieved_documents || []);
      }}

      /*
        You can also use renderTextResponse below, which allows you
        to modify the input bar while keeping additional default
        functionality such as the ability to trigger custom forms
        and a done state.
        Or you can use renderResponse for more flexibility and implement
        those states yourself, as shown below with the done state:
      */
      // renderResponse={({ onMessageSend, inputMode, appContext }) =>
      //   inputMode === INPUT_MODE.DONE ? (
      //     <div className="response-type-module">
      //       <div className="response-bar">
      //         <h3>Thanks for completing the task!</h3>
      //         <button
      //           id="done-button"
      //           type="button"
      //           className="btn btn-primary btn-lg"
      //           onClick={() => appContext.onTaskComplete()}
      //         >
      //           <span
      //             className="glyphicon glyphicon-ok-circle"
      //             aria-hidden="true"
      //           />{" "}
      //           Done with this HIT
      //         </button>
      //       </div>
      //     </div>
      //   ) : (
      //     <CustomTextResponse
      //       onMessageSend={onMessageSend}
      //       active={inputMode === INPUT_MODE.READY_FOR_INPUT}
      //       messages={messages}
      //       key={lastMessageAnnotation}
      //       isLastMessageAnnotated={
      //         messages.length === 0 || lastMessageAnnotation !== undefined
      //       }
      //       lastMessageAnnotation={lastMessageAnnotation}
      //     />
      //   )
      // }




      renderMessage={({ message, idx, mephistoContext, appContext }) => {
        // Destructure sendLiveUpdate from mephistoContext
        const { sendLiveUpdate } = mephistoContext;

        // Define a function for handling message regeneration or sending
        const handleRegenerate = (message, reason) => {
          const messageToSend = `REGENERATE: ${message.text} REASON: ${reason}`;
          // Use sendLiveUpdate directly from mephistoContext
          sendLiveUpdate({ text: "", task_data: { messageToSend } })
            .then(() => {
              console.log("Regenerate request sent successfully");
              message.text = ""
            })
            .catch((error) => {
              console.error("Error sending regenerate request", error);
              throw error;
            });
        };

        return (
          <RenderChatMessage
            message={message}
            isLastMessage={idx === messages.length - 1}
            mephistoContext={mephistoContext}
            appContext={appContext}
            onRegenerate={(reason) => handleRegenerate(message, reason)}
          />
        );
      }}


      renderSidePane={({ mephistoContext: { taskConfig } }) => (
        <StatementList statements={documents} />
      )}
    />
  );
}

export default MainApp;
