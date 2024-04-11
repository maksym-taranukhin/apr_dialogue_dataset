import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Editor, EditorState, convertToRaw, Modifier, getDefaultKeyBinding } from 'draft-js';
import 'draft-js/dist/Draft.css'; // Import Draft.js styles
import { Button } from 'react-bootstrap';

function useMessageSender(onMessageSend) {
    const [isSending, setIsSending] = useState(false);

    const sendMessage = useCallback((textValue) => {
        if (!textValue) return;
        setIsSending(true);
        onMessageSend({ text: textValue, task_data: {} })
            .finally(() => setIsSending(false));
    }, [onMessageSend]);

    return { isSending, sendMessage };
}

function CustomTextResponse({ onMessageSend, active, appendText }) {
    const [editorState, setEditorState] = useState(() => EditorState.createEmpty());
    const [isFocused, setIsFocused] = useState(false);
    const { isSending, sendMessage } = useMessageSender(onMessageSend);
    const editor = useRef(null);

    useEffect(() => {
        if (active && editor.current) editor.current.focus();
    }, [active]);

    // Effect to append text when appendText changes
    useEffect(() => {
        if (appendText) {
            const currentContent = editorState.getCurrentContent();
            const currentSelection = editorState.getSelection();
            const newContent = Modifier.insertText(
                currentContent,
                currentSelection,
                appendText
            );
            const newEditorState = EditorState.push(editorState, newContent, 'insert-characters');
            setEditorState(newEditorState);
        }
    }, [appendText]); // Only re-run if appendText changes

    const focusEditor = () => {
        editor.current.focus();
    };

    const onEditorChange = (newEditorState) => {
        setEditorState(newEditorState);
    };

    const handleSendMessage = () => {
        const contentState = editorState.getCurrentContent();
        const rawContent = convertToRaw(contentState);
        const textValue = rawContent.blocks.map(block => block.text).join('\n');
        sendMessage(textValue);
        setEditorState(EditorState.createEmpty()); // Reset editor after sending
    };

    // Custom key binding function to intercept the Enter key
    const myKeyBindingFn = (e) => {
        if (e.keyCode === 13) { // Check for Enter key
            handleSendMessage();
            return null; // Tell Draft.js we've handled this command
        }
        return getDefaultKeyBinding(e); // Use Draft.js's default key bindings for other keys
    };

    return (
        <div className="response-type-module" onClick={focusEditor}>
            <div className="response-bar">
                <div className={`response-text-input ${isFocused ? 'focus' : ''}`}>
                    <div className="resizable-editor-container">
                        <Editor
                            ref={editor}
                            editorState={editorState}
                            onChange={onEditorChange}
                            placeholder="Enter your response here..."
                            readOnly={isSending}
                            keyBindingFn={myKeyBindingFn} // Use the custom key binding function
                            onFocus={() => setIsFocused(true)}
                            onBlur={() => setIsFocused(false)}
                        />
                    </div>
                </div>
                <Button
                    className="btn btn-primary submit-response"
                    disabled={isSending || editorState.getCurrentContent().hasText() === false}
                    onClick={handleSendMessage}
                >
                    Send
                </Button>
            </div>
        </div>
    );
}


// import React, { useState, useEffect, useRef, useCallback } from "react";
// import { FormControl, Button } from "react-bootstrap";

// import { DndProvider } from 'react-dnd';
// import { HTML5Backend } from 'react-dnd-html5-backend';

// // Custom hook for handling message sending
// function useMessageSender(onMessageSend) {
//     const [isSending, setIsSending] = useState(false);

//     const sendMessage = useCallback((textValue) => {
//         if (!textValue) return;
//         setIsSending(true);
//         onMessageSend({ text: textValue, task_data: {} })
//             .finally(() => setIsSending(false));
//     }, [onMessageSend]);

//     return { isSending, sendMessage };
// }

// function CustomTextResponse({ onMessageSend, active }) {
//     const [textValue, setTextValue] = useState("");

//     const [spans, setSpans] = useState([
//         { id: 'span1', text: 'First Span' },
//         { id: 'span2', text: 'Second Span' }
//     ]); // To store span objects

//     const inputRef = useRef(null);
//     const { isSending, sendMessage } = useMessageSender(onMessageSend);

//     useEffect(() => {
//         if (active && inputRef.current && inputRef.current.focus) inputRef.current?.focus();
//     }, [active]);

//     // Handle drag start
//     const handleDragStart = (e, id) => {
//         e.dataTransfer.setData("text/plain", id);
//     };

//     // Handle drop
//     const handleDrop = (e) => {
//         e.preventDefault();
//         const id = e.dataTransfer.getData("text/plain");
//         const draggedSpan = spans.find(span => span.id === parseInt(id));
//         if (!draggedSpan) return;
//         // This example assumes you'll process or reposition the span in some way
//         console.log('Dropped span:', draggedSpan);
//         // For simplicity, the drop logic is not fully implemented
//     };

//     // Handle drag over
//     const handleDragOver = (e) => {
//         e.preventDefault(); // Necessary for the drop event to fire
//     };

//     // Remove span by id
//     const removeSpan = (id) => {
//         setSpans(spans.filter(span => span.id !== id));
//     };

//     return (
//         <DndProvider backend={HTML5Backend}>
//             <div className="response-type-module" onDrop={handleDrop} onDragOver={handleDragOver}>
//                 <div className="response-bar">
//                     {/* {spans.map((span) => (
//                         <span
//                             key={span.id}
//                             draggable
//                             onDragStart={(e) => handleDragStart(e, span.id)}
//                             style={{ margin: '0 5px', padding: '2px 5px', backgroundColor: '#007bff', color: 'white' }}>
//                             {span.text}
//                             <button onClick={() => removeSpan(span.id)} style={{ marginLeft: '5px', cursor: 'pointer' }}>×</button>
//                         </span>
//                     ))} */}
//                     <FormControl
//                         type="text"
//                         className="response-text-input"
//                         ref={inputRef}
//                         value={textValue}
//                         placeholder="Enter your response here..."
//                         onChange={(e) => setTextValue(e.target.value)}
//                         disabled={isSending}
//                         aria-label="Response Input"
//                     />
//                     <Button
//                         className="btn btn-primary submit-response"
//                         disabled={!textValue || isSending}
//                         onClick={() => { sendMessage(textValue); setTextValue(""); }}
//                     >
//                         Send
//                     </Button>
//                 </div>
//             </div>
//         </DndProvider>
//     );
// }


// function CustomTextResponse({ onMessageSend, active, selectedSpans }) {
//     const [textValue, setTextValue] = useState("");
//     const inputRef = useRef(null);
//     const { isSending, sendMessage } = useMessageSender(onMessageSend);

//     useEffect(() => {
//         if (active) inputRef.current?.focus();
//     }, [active]);

//     useEffect(() => {
//         if (responseText !== undefined && responseText !== textValue) {
//             setTextValue(responseText);
//         }
//     }, [responseText, textValue]);

//     const handleKeyDown = useCallback((e) => {
//         if (e.key === "Enter") {
//             e.preventDefault();
//             sendMessage(textValue);
//             setTextValue(""); // Reset textValue here to clear the input after sending
//         }
//     }, [sendMessage, textValue]);

//     return (
//         <div className="response-type-module">
//             <div className="response-bar">
//                 <FormControl
//                     type="text"
//                     className="response-text-input"
//                     ref={inputRef}
//                     value={textValue}
//                     placeholder="Enter your response here..."
//                     onKeyDown={handleKeyDown}
//                     onChange={(e) => setTextValue(e.target.value)}
//                     disabled={isSending}
//                     aria-label="Response Input"
//                 />
//                 <Button
//                     className="btn btn-primary submit-response"
//                     id="id_send_msg_button"
//                     disabled={!textValue || isSending}
//                     onClick={() => { sendMessage(textValue); setTextValue(""); }}
//                 >
//                     Send
//                 </Button>
//             </div>
//         </div>
//     );
// }

export default CustomTextResponse;
