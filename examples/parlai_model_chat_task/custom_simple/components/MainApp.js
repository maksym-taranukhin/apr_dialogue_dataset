/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import "bootstrap-chat/styles.css";
import { ChatApp, DefaultTaskDescription, INPUT_MODE } from "bootstrap-chat";
import RenderChatMessage from "./RenderChatMessage";
import CustomTextResponse from "./CustomTextResponse";
import StatementList from "./StatementList";

function MainApp() {
  const [messages, setMessages] = React.useState([]);
  const [chatAnnotations, setChatAnnotation] = React.useReducer(
    (state, action) => {
      return { ...state, ...{ [action.index]: action.value } };
    },
    {}
  );

  const lastMessageAnnotation = chatAnnotations[messages.length - 1];

  return (
    <ChatApp
      onMessagesChange={(messages) => {
        setMessages(messages);
      }}
      /*
        You can also use renderTextResponse below, which allows you
        to modify the input bar while keeping additional default
        functionality such as the ability to trigger custom forms
        and a done state.
        Or you can use renderResponse for more flexibility and implement
        those states yourself, as shown below with the done state:
      */
      renderResponse={({ onMessageSend, inputMode, appContext }) =>
        inputMode === INPUT_MODE.DONE ? (
          <div className="response-type-module">
            <div className="response-bar">
              <h3>Thanks for completing the task!</h3>
              <button
                id="done-button"
                type="button"
                className="btn btn-primary btn-lg"
                onClick={() => appContext.onTaskComplete()}
              >
                <span
                  className="glyphicon glyphicon-ok-circle"
                  aria-hidden="true"
                />{" "}
                Done with this HIT
              </button>
            </div>
          </div>
        ) : (
          <CustomTextResponse
            onMessageSend={onMessageSend}
            active={inputMode === INPUT_MODE.READY_FOR_INPUT}
            messages={messages}
            key={lastMessageAnnotation}
            isLastMessageAnnotated={
              messages.length === 0 || lastMessageAnnotation !== undefined
            }
            lastMessageAnnotation={lastMessageAnnotation}
          />
        )
      }
      renderMessage={({ message, idx, mephistoContext, appContext }) => (
        <RenderChatMessage
          message={message}
          mephistoContext={mephistoContext}
          appContext={appContext}
          idx={idx}
          key={message.update_id + "-" + idx}
          onRadioChange={(val) => {
            setChatAnnotation({ index: idx, value: val });
          }}
        />
      )}
      renderSidePane={({ mephistoContext: { taskConfig } }) => (

        // show a list of suggested responses
        // <div>
        //   <h3>Suggested Responses</h3>
        //   <ul>
        //     <li>I'm sorry, I don't understand.</li>
        //     <li>Can you please rephrase that?</li>
        //     <li>I'm not sure what you mean.</li>
        //     <li>I'm not sure how to respond to that.</li>
        //   </ul>
        // </div>


        // show a list of suggested responses
        // <StatementList>
        //   {[
        //     "I'm sorry, I don't understand.",
        //     "Can you please rephrase that?",
        //     "I'm not sure what you mean.",
        //     "I'm not sure how to respond to that.",

        //   ]}
        // </StatementList>

        <DefaultTaskDescription
          chatTitle={taskConfig.chat_title}
          taskDescriptionHtml={taskConfig.task_description}
        >
          <div>
            <h3>Suggested Responses</h3>
            <ul>
              <li>I'm sorry, I don't understand.</li>
              <li>Can you please rephrase that?</li>
              <li>I'm not sure what you mean.</li>
              <li>I'm not sure how to respond to that.</li>
            </ul>
          </div>
        </DefaultTaskDescription>
      )}
    />
  );
}

export default MainApp;
