import { component$, Slot } from '@builder.io/qwik';

export const Card = component$<{ class?: string }>((props) => {
  return (
    <div class={`bg-white rounded-lg border border-gray-200 shadow-sm ${props.class || ''}`}>
      <Slot />
    </div>
  );
});

export const CardHeader = component$<{ class?: string }>((props) => {
  return (
    <div class={`px-4 sm:px-6 py-4 sm:py-5 border-b border-gray-200 ${props.class || ''}`}>
      <Slot />
    </div>
  );
});

export const CardBody = component$<{ class?: string }>((props) => {
  return (
    <div class={`px-4 sm:px-6 py-4 sm:py-5 ${props.class || ''}`}>
      <Slot />
    </div>
  );
});

export const CardFooter = component$<{ class?: string }>((props) => {
  return (
    <div class={`px-4 sm:px-6 py-4 sm:py-5 border-t border-gray-200 bg-gray-50 rounded-b-lg ${props.class || ''}`}>
      <Slot />
    </div>
  );
});

export const CardTitle = component$<{ class?: string }>((props) => {
  return (
    <h3 class={`text-base sm:text-lg font-semibold text-gray-900 ${props.class || ''}`}>
      <Slot />
    </h3>
  );
});

export const CardDescription = component$<{ class?: string }>((props) => {
  return (
    <p class={`text-sm text-gray-600 ${props.class || ''}`}>
      <Slot />
    </p>
  );
});

export const StatCard = component$<{
  title: string;
  value: string | number;
  icon?: any;
  color?: 'blue' | 'green' | 'purple' | 'yellow' | 'red';
  class?: string;
}>((props) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100', 
    purple: 'text-purple-600 bg-purple-100',
    yellow: 'text-yellow-600 bg-yellow-100',
    red: 'text-red-600 bg-red-100'
  };
  
  const iconColorClass = colorClasses[props.color || 'blue'];
  
  return (
    <Card class={props.class}>
      <CardBody class="flex items-center justify-between">
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-600 truncate">{props.title}</p>
          <p class="text-xl sm:text-2xl font-bold text-gray-900 mt-1">{props.value}</p>
        </div>
        {props.icon && (
          <div class={`p-2 sm:p-3 rounded-lg ${iconColorClass}`}>
            {props.icon}
          </div>
        )}
      </CardBody>
    </Card>
  );
});

export const CardGrid = component$<{ 
  cols?: '1' | '2' | '3' | '4' | '6';
  class?: string;
}>((props) => {
  const colsClass = {
    '1': 'grid-cols-1',
    '2': 'grid-cols-1 sm:grid-cols-2', 
    '3': 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    '4': 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
    '6': 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-6'
  };
  
  return (
    <div class={`grid gap-4 sm:gap-6 ${colsClass[props.cols || '3']} ${props.class || ''}`}>
      <Slot />
    </div>
  );
}); 