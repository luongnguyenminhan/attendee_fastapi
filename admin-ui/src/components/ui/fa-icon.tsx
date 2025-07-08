import { component$ } from '@builder.io/qwik';
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core';

export const FaIcon = component$<{
  icon: IconDefinition;
  class?: string;
}>((props) => {
  const { icon } = props;
  const [width, height, , , svgPathData] = icon.icon;
  
  return (
    <svg
      class={`fill-current ${props.class || 'h-5 w-5'}`}
      viewBox={`0 0 ${width} ${height}`}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d={svgPathData as string} />
    </svg>
  );
}); 