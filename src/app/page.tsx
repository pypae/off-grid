"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

export default async function Page() {
  const Map = useMemo(
    () =>
      dynamic(() => import("@/components/map"), {
        ssr: false,
      }),
    []
  );

  return (
    <div className="container mx-auto h-screen">
      <div className="flex flex-col bg-white-700 h-full py-4">
        <div className="flex-none mx-2 mb-4">
          <h1 className="text-2xl font-bold mb-2">
            Demo — Pathfinding based on Classified Avalanche Terrain
          </h1>
          <p>
            Click on the map to select a start- and endpoint to compute the path
            with the lowest avalanche risk between them.
          </p>
          
        </div>
        <div className="grow">
          <Map posix={[46.802128, 9.833477]} />
        </div>
      </div>
    </div>
  );
}
