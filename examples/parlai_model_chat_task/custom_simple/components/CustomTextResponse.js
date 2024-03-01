import React from "react";
import { FormControl, Button } from "react-bootstrap";

function CustomTextResponse({
    onMessageSend,
    active,
    isLastMessageAnnotated,
    lastMessageAnnotation,
}) {
    const [textValue, setTextValue] = React.useState(
        !lastMessageAnnotation ? "" : lastMessageAnnotation + " - "
    );
    const [sending, setSending] = React.useState(false);

    const annotationNeeded = active && !isLastMessageAnnotated;
    active = active && isLastMessageAnnotated;

    const inputRef = React.useRef();

    React.useEffect(() => {
        if (active && inputRef.current && inputRef.current.focus) {
            inputRef.current.focus();
        }
    }, [active]);

    const tryMessageSend = React.useCallback(() => {
        if (textValue !== "" && active && !sending) {
            setSending(true);
            onMessageSend({ text: textValue, task_data: {} }).then(() => {
                setTextValue("");
                setSending(false);
            });
        }
    }, [textValue, active, sending, onMessageSend]);

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
                <FormControl
                    type="text"
                    className="response-text-input"
                    inputRef={(ref) => {
                        inputRef.current = ref;
                    }}
                    value={textValue}
                    placeholder={
                        annotationNeeded
                            ? "Please annotate the last message before you can continue"
                            : "Enter your message here..."
                    }
                    onKeyPress={(e) => handleKeyPress(e)}
                    onChange={(e) => setTextValue(e.target.value)}
                    disabled={!active || sending}
                />
                <Button
                    className="btn btn-primary submit-response"
                    id="id_send_msg_button"
                    disabled={textValue === "" || !active || sending}
                    onClick={() => tryMessageSend()}
                >
                    Send
                </Button>
            </div>
        </div>
    );
}

export default CustomTextResponse;
