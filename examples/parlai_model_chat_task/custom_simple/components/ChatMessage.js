import React from "react";
import { FormGroup, Radio } from "react-bootstrap";

function ChatMessage({ isSelf, idx, agentName, message = "", onRadioChange }) {
    const floatToSide = isSelf ? "right" : "left";
    const alertStyle = isSelf ? "alert-info" : "alert-warning";

    const handleChange = (e) => {
        onRadioChange(e.currentTarget.value);
    };

    return (
        <div className="row" style={{ marginLeft: "0", marginRight: "0" }}>
            <div
                className={"alert message " + alertStyle}
                role="alert"
                style={{ float: floatToSide }}
            >
                <span style={{ fontSize: "16px", whiteSpace: "pre-wrap" }}>
                    <b>{agentName}</b>: {message}
                </span>
                {isSelf ? null : (
                    <FormGroup>
                        <Radio
                            name={"radio" + idx}
                            value={"The message is inconsistent with the conversation."}
                            inline
                            onChange={handleChange}
                        >
                            The message is inconsistent with the conversation.
                        </Radio>{" "}
                        <Radio
                            name={"radio" + idx}
                            value={"The message contains factual errors."}
                            inline
                            onChange={handleChange}
                        >
                            The message contains factual errors.
                        </Radio>
                    </FormGroup>
                )}
            </div>
        </div>
    );
}

export default ChatMessage;
