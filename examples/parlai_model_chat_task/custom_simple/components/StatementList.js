import React from 'react';
import { ListGroup, ListGroupItem } from 'react-bootstrap';
import { useMemo } from 'react';

const StatementList = ({ statements }) => {
    // statements is an array of dictionaries with the following keys:
    // - id: the id of the statement
    // - title: the title of the statement
    // - text: the text of the statement
    // - score: the score of the statement

    return (
        <ListGroup style={{ width: '100%' }}>
            {statements.map((statement, index) => {
                // show the statement title and text in the list
                const htmlContent = {
                    __html: `<strong>${statement.title}</strong>: ${statement.text}<br/>score: ${statement.score}`
                };

                return (
                    <ListGroupItem
                        key={statement.id}
                        style={{
                            backgroundColor: index % 2 === 0 ? '#f8f9fa' : '#e9ecef',
                            width: '100%', // Ensure full width
                            wordWrap: 'break-word' // Handle long texts
                        }}
                        dangerouslySetInnerHTML={htmlContent}
                    />
                );
            })}
        </ListGroup>
    );
};

export default React.memo(StatementList);
