"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import { FaGithub } from "react-icons/fa";

export default async function Page() {
  const Map = useMemo(
    () =>
      dynamic(() => import("@/components/map"), {
        ssr: false,
      }),
    []
  );

  return (
    <div className="container mx-auto h-screen sm:px-4 sm:py-6">
      <div className="flex flex-col bg-white dark:bg-gray-800 shadow-lg h-full overflow-hidden sm:rounded-lg sm:border-b sm:border-gray-200 dark:sm:border-gray-700">
        <div className="flex items-center justify-between px-6 py-4 bg-gray-100 dark:bg-gray-700">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
              Off-Grid: Experimental Ski Tour Route Planner
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              This demo tool uses{" "}
              <a
                href="https://content.whiterisk.ch/en/help/maps/classified-avalanche-terrain-cat"
                target="_blank"
                className="text-blue-500 underline dark:text-blue-400"
              >
                categorical avalanche terrain
              </a>{" "}
              data and an{" "}
              <a
                href="https://www.redblobgames.com/pathfinding/a-star/introduction.html"
                target="_blank"
                className="text-blue-500 underline dark:text-blue-400"
              >
                A* algorithm
              </a>{" "}
              to find low-risk ski routes in Switzerland.
            </p>
          </div>
          <a
            href="https://github.com/pypae/off-grid"
            target="_blank"
            rel="noopener noreferrer"
            className="ml-4 flex items-center text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white"
          >
            <FaGithub size={24} />
            <span className="ml-2 hidden lg:block">Code & Documentation</span>
          </a>
        </div>

        <div className="p-6 text-gray-700 dark:text-gray-300">
          <p>
            Select start and end points on the map below to calculate the safest
            route.
          </p>
          <p className="text-xs mt-2 text-gray-500 dark:text-gray-400">
            To plan actual ski tours, please use{" "}
            <a
              href="https://whiterisk.ch/"
              target="_blank"
              className="text-blue-500 underline dark:text-blue-400"
            >
              White Risk
            </a>{" "}
            or{" "}
            <a
              href="https://www.skitourenguru.ch/"
              target="_blank"
              className="text-blue-500 underline dark:text-blue-400"
            >
              Skitourenguru
            </a>
            .
          </p>
        </div>

        <div className="flex-grow h-full">
          <Map posix={[46.802128, 9.833477]} />
        </div>
      </div>
    </div>
  );
}
