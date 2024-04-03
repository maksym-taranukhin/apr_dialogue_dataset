import React from 'react';
import { Button, Glyphicon } from 'react-bootstrap';

const RegenerateButton = ({ onClick, active }) => (
    <Button
        onClick={onClick}
        style={{
            opacity: 0.7,
            marginLeft: '10px',
        }}
        onMouseOver={(e) => (e.currentTarget.style.opacity = 1)} // Non-transparent on hover
        onMouseOut={(e) => (e.currentTarget.style.opacity = 0.7)} // Revert transparency

        disabled={!active} // Enable the button
    >
        <Glyphicon glyph="refresh" />
    </Button>
);

export default RegenerateButton;
