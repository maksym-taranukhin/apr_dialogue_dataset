import React from "react";
import ChatMessage from "./ChatMessage";

function RenderChatMessage({
    message,
    mephistoContext,
    appContext,
    idx,
    onRadioChange,
}) {
    const { agentId } = mephistoContext;
    const { currentAgentNames } = appContext.taskContext;

    return (
        <div>
            <ChatMessage
                idx={idx}
                isSelf={message.id === agentId || message.id in currentAgentNames}
                agentName={
                    message.id in currentAgentNames
                        ? currentAgentNames[message.id]
                        : message.id
                }
                message={message.text}
                taskData={message.task_data}
                messageId={message.update_id}
                onRadioChange={onRadioChange}
            />
        </div>
    );
}

export default RenderChatMessage;
