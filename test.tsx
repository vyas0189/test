'use client'

import React, { useState } from 'react'
import { Moon, Sun } from 'lucide-react'

type Category = {
  name: string;
  description: string;
}

type Pillar = {
  name: string;
  description: string;
  categories: Category[];
}

const mockApiResponse: Pillar[] = [
  {
    name: "Technology",
    description: "Cutting-edge advancements shaping our future",
    categories: [
      { name: "AI", description: "Artificial Intelligence and machine learning innovations revolutionizing industries and daily life through advanced algorithms and data processing capabilities." },
      { name: "Blockchain", description: "Decentralized and secure transaction technologies enabling transparent and tamper-proof record-keeping across various sectors." },
      { name: "Cloud Computing", description: "Scalable and flexible online computing services providing on-demand access to a shared pool of configurable computing resources." },
      { name: "IoT", description: "Internet of Things and connected smart devices creating a network of physical objects embedded with sensors, software, and network connectivity." },
      { name: "5G", description: "Next-generation cellular network technology offering faster speeds, lower latency, and increased connectivity for mobile devices and IoT applications." }
    ]
  },
  {
    name: "Health",
    description: "Promoting wellness and advancing medical science",
    categories: [
      { name: "Nutrition", description: "Dietary science and healthy eating habits focusing on the impact of food on overall health and disease prevention." },
      { name: "Fitness", description: "Physical exercise and body conditioning strategies to improve strength, endurance, and overall well-being." },
      { name: "Mental Health", description: "Psychological well-being and therapy addressing emotional, psychological, and social aspects of mental wellness through various therapeutic approaches and interventions." }
    ]
  },
  {
    name: "Environment",
    description: "Protecting and preserving our planet's ecosystems",
    categories: [
      { name: "Renewable Energy", description: "Sustainable power sources and technologies harnessing natural resources like solar, wind, and hydroelectric power to reduce reliance on fossil fuels and combat climate change." },
      { name: "Conservation", description: "Preserving natural habitats and biodiversity through protected areas, wildlife management, and sustainable resource use practices." },
      { name: "Sustainable Agriculture", description: "Eco-friendly farming and food production methods that maintain soil health, minimize water use, and reduce the environmental impact of agricultural practices." },
      { name: "Waste Management", description: "Efficient handling and recycling of waste materials to minimize environmental pollution and promote circular economy principles." },
      { name: "Climate Change Mitigation", description: "Strategies to reduce global warming impact through emissions reduction, carbon capture, and adaptation measures to address the effects of climate change." },
      { name: "Water Conservation", description: "Preserving and managing water resources through efficient use, pollution prevention, and ecosystem protection to ensure long-term water security." },
      { name: "Air Quality", description: "Monitoring and improving air quality through reduction of pollutants and implementation of clean air technologies." },
      { name: "Biodiversity", description: "Protecting and preserving the variety of life on Earth, including genetic diversity within species and ecosystem diversity." },
      { name: "Ocean Conservation", description: "Efforts to protect and restore marine ecosystems, including coral reefs, mangroves, and ocean wildlife." },
      { name: "Sustainable Transportation", description: "Developing and promoting eco-friendly transportation options to reduce carbon emissions and improve urban air quality." },
      { name: "Green Building", description: "Designing and constructing buildings that are environmentally responsible and resource-efficient throughout their life-cycle." },
      { name: "Environmental Education", description: "Programs and initiatives to increase public awareness and understanding of environmental issues and sustainable practices." },
      { name: "Circular Economy", description: "Economic systems aimed at eliminating waste and the continual use of resources through recycling, reusing, and repurposing." },
      { name: "Sustainable Fashion", description: "Clothing and accessories created and consumed in a way that can be sustained while protecting both the environment and those producing them." },
      { name: "Eco-Tourism", description: "Responsible travel to natural areas that conserves the environment, sustains the well-being of the local people, and involves interpretation and education." },
      { name: "Sustainable Packaging", description: "Packaging solutions that are environmentally friendly, recyclable, and minimize waste throughout the product lifecycle." },
      { name: "Urban Greening", description: "Increasing the amount of green spaces in urban areas to improve air quality, reduce heat island effects, and enhance biodiversity." },
      { name: "Sustainable Fishing", description: "Fishing practices that maintain fish populations without harming the ecosystem or compromising the ability for future generations to meet their needs." },
      { name: "Environmental Law", description: "Legal frameworks and regulations designed to protect the environment and natural resources." },
      { name: "Green Technology", description: "Development and application of products, equipment, and systems used to conserve the natural environment and resources." }
    ]
  },
  {
    name: "Education",
    description: "Fostering learning and personal growth",
    categories: [
      { name: "Online Learning", description: "Digital platforms for remote education enabling access to courses and educational resources from anywhere in the world." },
      { name: "STEM", description: "Science, Technology, Engineering, and Mathematics focus in education to prepare students for careers in these high-demand fields." },
      { name: "Early Childhood", description: "Foundational learning for young children focusing on cognitive, social, and emotional development in the crucial early years." },
      { name: "Lifelong Learning", description: "Continuous education throughout adulthood to acquire new skills, adapt to changing job markets, and pursue personal interests and growth." }
    ]
  }
]

const CategoryCard: React.FC<{ category: Category; bgClass: string; textClass: string }> = ({ category, bgClass, textClass }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className={`p-3 rounded-md flex flex-col h-full ${bgClass} ${textClass} relative group`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onFocus={() => setIsHovered(true)}
      onBlur={() => setIsHovered(false)}
      tabIndex={0}
    >
      <h3 className="font-semibold mb-1 text-sm">{category.name}</h3>
      <p className="text-xs line-clamp-3 group-hover:line-clamp-none transition-all duration-300">
        {category.description}
      </p>
      {isHovered && (
        <div className="absolute inset-0 bg-card dark:bg-gray-800 text-card-foreground dark:text-gray-200 p-3 rounded-md overflow-y-auto shadow-lg z-10">
          <h3 className="font-semibold mb-1 text-sm">{category.name}</h3>
          <p className="text-xs">{category.description}</p>
        </div>
      )}
    </div>
  );
};

export default function Component() {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="container mx-auto p-4 dark:bg-[#0e4491] transition-colors duration-300">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold text-primary dark:text-white">Pillars and Categories</h1>
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
            aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
        </div>
        <div className="space-y-4">
          {mockApiResponse.map((pillar, index) => (
            <div 
              key={pillar.name} 
              className={`rounded-lg shadow-md overflow-hidden ${
                index % 2 === 0 
                  ? 'bg-card text-card-foreground dark:bg-gray-800 dark:text-gray-200' 
                  : 'bg-secondary text-secondary-foreground dark:bg-gray-700 dark:text-gray-200'
              }`}
            >
              <div className="p-4">
                <div className="flex flex-col md:flex-row md:items-center mb-3">
                  <h2 className="text-xl font-semibold mr-4">{pillar.name}</h2>
                  <p className={`text-sm ${index % 2 === 0 ? 'text-muted-foreground dark:text-gray-300' : 'text-secondary-foreground/80 dark:text-gray-300'}`}>
                    {pillar.description}
                  </p>
                </div>
                <div className={`grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 ${pillar.categories.length > 6 ? 'max-h-[400px] overflow-y-auto pr-2' : ''}`}>
                  {pillar.categories.map((category) => (
                    <CategoryCard 
                      key={category.name}
                      category={category}
                      bgClass={index % 2 === 0 ? 'bg-muted dark:bg-gray-700' : 'bg-secondary-foreground/10 dark:bg-gray-600'}
                      textClass={index % 2 === 0 ? 'text-muted-foreground dark:text-gray-200' : 'text-secondary-foreground dark:text-gray-200'}
                    />
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
