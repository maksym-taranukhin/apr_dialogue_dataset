import React from "react";
import { FormControl, Button } from "react-bootstrap";

function CustomTextResponse({
    onMessageSend,
    active,
    isLastMessageAnnotated,
    lastMessageAnnotation,
}) {
    const [textValue, setTextValue] = React.useState("");
    const [sending, setSending] = React.useState(false);

    // const annotationNeeded = active && !isLastMessageAnnotated;
    active = active && isLastMessageAnnotated;

    const inputRef = React.useRef();

    React.useEffect(() => {
        if (active && inputRef.current && inputRef.current.focus) {
            inputRef.current.focus();
        }
    }, [active]);

    const tryMessageSend = React.useCallback((regenerate = false) => {
        let messageToSend = textValue;
        if (regenerate && lastMessageAnnotation) {
            messageToSend = `REGENERATE: ${lastMessageAnnotation}`;
            setTextValue(""); // Clearing the text field
        }

        if (messageToSend !== "" && !sending) {
            setSending(true);
            onMessageSend({ text: messageToSend, task_data: {} }).then(() => {
                setSending(false);
                setTextValue(""); // Clearing the text field
            });
        }
    }, [textValue, active, sending, onMessageSend, lastMessageAnnotation]);

    const handleKeyPress = React.useCallback(
        (e) => {
            if (e.key === "Enter") {
                tryMessageSend();
                e.stopPropagation();
                e.nativeEvent.stopImmediatePropagation();
            }
        },
        [tryMessageSend]
    );

    return (
        <div className="response-type-module">
            <div className="response-bar">

                <Button
                    className="btn btn-warning"
                    id="id_regenerate_msg_button"
                    onClick={() => tryMessageSend(true)}
                    disabled={sending || !isLastMessageAnnotated}
                >
                    Regenerate
                </Button>
                <FormControl
                    type="text"
                    className="response-text-input"
                    inputRef={(ref) => {
                        inputRef.current = ref;
                    }}
                    value={textValue}
                    placeholder={"Enter your response here..."}
                    onKeyPress={(e) => handleKeyPress(e)}
                    onChange={(e) => setTextValue(e.target.value)}
                    disabled={sending}
                />
                <Button
                    className="btn btn-primary submit-response"
                    id="id_send_msg_button"
                    disabled={textValue === "" || sending}
                    onClick={() => tryMessageSend()}
                >
                    Send
                </Button>
            </div>
        </div>
    );
}

export default CustomTextResponse;
