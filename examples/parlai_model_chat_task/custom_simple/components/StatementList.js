import React from 'react';
import { ListGroup, ListGroupItem } from 'react-bootstrap';

const StatementList = ({ statements, onSpanSelected }) => {
    // Modified handleRightClick function to accept additional statement details
    const handleRightClick = (event, id, title, score, source) => {
        event.preventDefault(); // Prevent the default context menu from showing

        const selectedText = window.getSelection().toString().trim();
        if (selectedText) {
            onSpanSelected({ id, title, score, source, selectedText });
        }
    };

    if (!statements?.length) {
        return (
            <ListGroup style={{ width: '100%' }}>
                <ListGroupItem>No documents available.</ListGroupItem>
            </ListGroup>
        );
    }

    return (
        <ListGroup style={{ width: '100%' }}>
            {statements.map(({ id, title, text, score, source }, index) => {
                if (!id || !title || !text || !score ) return null;

                const listItemStyle = {
                    backgroundColor: index % 2 === 0 ? '#f8f9fa' : '#e9ecef',
                    width: '100%',
                    wordWrap: 'break-word',
                    cursor: 'context-menu', // Indicate that right-click is available
                };

                const htmlContent = {
                    __html: `<strong>${title}</strong>: ${text}<br/><strong>score</strong>: ${(score * 100).toFixed(2)}<br/><a href="${source}" target="_blank">Source</a>`,
                };

                return (
                    <ListGroupItem
                        key={id}
                        style={listItemStyle}
                        dangerouslySetInnerHTML={htmlContent}
                        // Update the event handler to pass the statement details
                        onContextMenu={(event) => handleRightClick(event, id, title, score, source)}
                    />
                );
            })}
        </ListGroup>
    );
};

export default React.memo(StatementList);
