import React from 'react';
import { ListGroup } from 'react-bootstrap';

const StatementList = ({ statements }) => {
    return (
        <ListGroup>
            {statements.map((statement, index) => (
                <ListGroup.Item
                    key={index}
                    style={{
                        backgroundColor: index % 2 === 0 ? '#f8f9fa' : '#e9ecef', // Bootstrap-like shades of gray
                    }}
                >
                    {statement}
                </ListGroup.Item>
            ))}
        </ListGroup>
    );
};

export default StatementList;
