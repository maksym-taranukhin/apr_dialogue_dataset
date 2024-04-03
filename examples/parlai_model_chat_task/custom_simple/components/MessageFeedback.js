import React, { useState } from 'react';
import { Button, Tooltip, OverlayTrigger, Form, FormGroup, FormControl, InputGroup, Glyphicon } from 'react-bootstrap';

const FeedbackComponent = ({ onRegenerate }) => {
    const [feedbackText, setFeedbackText] = useState('');

    const handleSubmitFeedback = (reason) => {
        onRegenerate(reason); // Call the provided onRegenerate function with the reason
        setFeedbackText(''); // Reset the feedback text field after submission
    };

    const tooltips = {
        understanding: (
            <Tooltip id="tooltip-understanding">This message was informative or enlightening.</Tooltip>
        ),
        helpfulness: (
            <Tooltip id="tooltip-helpfulness">This message was helpful.</Tooltip>
        ),
        relevance: (
            <Tooltip id="tooltip-relevance">This message was relevant to my query.</Tooltip>
        ),
    };

    return (
        <div>
            <OverlayTrigger placement="top" overlay={tooltips.understanding}>
                <Button onClick={() => handleSubmitFeedback('Understanding')} variant="light">
                    <Glyphicon glyph="lightbulb" />
                </Button>
            </OverlayTrigger>

            <OverlayTrigger placement="top" overlay={tooltips.helpfulness}>
                <Button onClick={() => handleSubmitFeedback('Helpfulness')} variant="light">
                    <Glyphicon glyph="thumbs-up" />
                </Button>
            </OverlayTrigger>

            <OverlayTrigger placement="top" overlay={tooltips.relevance}>
                <Button onClick={() => handleSubmitFeedback('Relevance')} variant="light">
                    <Glyphicon glyph="screenshot" />
                </Button>
            </OverlayTrigger>

            <Form
                inline
                onSubmit={(e) => {
                    e.preventDefault(); // Prevent the form from causing a page reload
                    handleSubmitFeedback(feedbackText);
                }}
            >
                <FormGroup>
                    <InputGroup>
                        <FormControl
                            type="text"
                            value={feedbackText}
                            onChange={(e) => setFeedbackText(e.target.value)}
                            placeholder="Other feedback..."
                        />
                        <InputGroup.Button>
                            <Button type="submit">
                                <Glyphicon glyph="send" />
                            </Button>
                        </InputGroup.Button>
                    </InputGroup>
                </FormGroup>
            </Form>
        </div>
    );
};

export default FeedbackComponent;
