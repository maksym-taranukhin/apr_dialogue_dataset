import React from "react";
import RegenerateButton from './RegenerateButton';

function ChatMessage({ isSelf, agentName, message = "", isLastMessage, onRegenerate }) {
    const [isButtonActive, setIsButtonActive] = React.useState(true);

    const handleRegenerate = (reason = "") => {
        setIsButtonActive(false);
        try { onRegenerate(reason)} catch (error) {
            console.error("Regeneration failed:", error);
            setIsButtonActive(true);
        }
    };

    // Conditional class appending based on isSelf
    const messageStyleClass = `message-style ${isSelf ? '' : 'opponent'}`;
    const agentNameClass = `agent-name ${isSelf ? '' : 'opponent'}`;
    const messageContainerClass = `message-container ${isSelf ? '' : 'opponent'}`;

    return (
        <div style={{ display: 'flex', justifyContent: isSelf ? 'flex-end' : 'flex-start', width: '100%', padding: '5px 0' }}>
            <div style={{ width: '100%' }} className={!isButtonActive ? 'regenerating-message' : ''}>
                <div className={agentNameClass}>{agentName}</div>
                <div className={messageContainerClass}>
                    <div className={messageStyleClass}>{message}</div>
                    {!isSelf && isLastMessage && <RegenerateButton onClick={handleRegenerate} active={isButtonActive} />}
                </div>
            </div>
        </div>
    );
}
export default ChatMessage;
