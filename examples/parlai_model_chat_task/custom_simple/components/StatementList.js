import React from 'react';
import { ListGroup, ListGroupItem } from 'react-bootstrap';

const StatementList = ({ statements }) => {
    // statements is an array of dictionaries with the following keys:
    // - id: the id of the statement
    // - title: the title of the statement
    // - text: the text of the statement
    // - score: the score of the statement

    // Early return for null, undefined, or empty statements
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
                // Skip rendering if essential properties are missing
                if (!id || !title || text === undefined || score === undefined) return null;

                const listItemStyle = {
                    backgroundColor: index % 2 === 0 ? '#f8f9fa' : '#e9ecef',
                    width: '100%',
                    wordWrap: 'break-word',
                };

                const htmlContent = {
                    __html: `<strong>${title}</strong>: ${text}<br/><strong>score</strong>: ${(score * 100).toFixed(2)}<br/><a href="${source}" target="_blank">${source}</a>`,
                };

                return (
                    <ListGroupItem
                        key={id}
                        style={listItemStyle}
                        dangerouslySetInnerHTML={htmlContent}
                    />
                );
            })}
        </ListGroup>
    );
};

export default React.memo(StatementList);
