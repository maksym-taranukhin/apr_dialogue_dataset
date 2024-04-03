import React from "react";
import ChatMessage from "./ChatMessage";

function RenderChatMessage({
    message,
    isLastMessage,
    mephistoContext,
    appContext,
    onRegenerate
}) {
    const { agentId } = mephistoContext;
    const { currentAgentNames } = appContext.taskContext;

    // Check if message.text is empty or not defined
    if (!message.text) {
        // Return null or an alternative component to avoid rendering
        return null;
    }

    return (
        <div>
            <ChatMessage
                isSelf={message.id === agentId || message.id in currentAgentNames}
                agentName={
                    message.id in currentAgentNames
                        ? currentAgentNames[message.id]
                        : message.id
                }
                message={message.text}
                isLastMessage={isLastMessage}
                onRegenerate={onRegenerate}
                // taskData={message.task_data}
                // messageId={message.update_id}
            />
        </div>
    );
}

export default RenderChatMessage;
