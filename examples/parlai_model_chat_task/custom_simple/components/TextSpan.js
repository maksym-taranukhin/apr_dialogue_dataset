import { useDrag } from 'react-dnd';

const UnmodifiableTextSpan = ({ id, text }) => {
    const [{ isDragging }, drag] = useDrag(() => ({
        type: 'span',
        item: { id, text },
        collect: (monitor) => ({
            isDragging: !!monitor.isDragging(),
        }),
    }));

    return (
        <span
            ref={drag}
            style={{
                opacity: isDragging ? 0.5 : 1,
                backgroundColor: '#007bff',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '4px',
                cursor: 'move',
            }}
        >
            {text}
        </span>
    );
};

export default UnmodifiableTextSpan;
