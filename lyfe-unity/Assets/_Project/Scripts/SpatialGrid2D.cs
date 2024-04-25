using System.Collections.Generic;
using UnityEngine;

public class SpatialGrid2D
{
    private Vector2 gridSize;
    private Dictionary<Vector2, List<GameObject>> cells;

    public SpatialGrid2D(Vector2 gridSize)
    {
        this.gridSize = gridSize;
        this.cells = new Dictionary<Vector2, List<GameObject>>();
    }

    public void Insert(GameObject entity)
    {
        Vector2 cell = GetCellForPosition(entity.transform.position);
        if (!cells.TryGetValue(cell, out var entitiesInCell))
        {
            entitiesInCell = new List<GameObject>();
            cells[cell] = entitiesInCell;
        }
        entitiesInCell.Add(entity);
    }

    public void Remove(GameObject entity, Vector2 cell)
    {
        if (cells.TryGetValue(cell, out var entitiesInCell))
        {
            entitiesInCell.Remove(entity);
        }
    }

    public Vector2 AddEntity(GameObject entity)
    {
        Vector2 cell = GetCellForPosition(entity.transform.position);
        Insert(entity);
        return cell;
    }

    public Vector2 UpdateEntity(GameObject entity, Vector2 oldCell)
    {
        Vector2 newCell = GetCellForPosition(entity.transform.position);
        if (newCell != oldCell)
        {
            Remove(entity, oldCell);
            Insert(entity);
        }
        return newCell;
    }


    public List<GameObject> QueryNearbyEntities(GameObject entity, float radius)
    {
        Vector2 cell = GetCellForPosition(entity.transform.position);
        List<GameObject> nearbyEntities = new List<GameObject>();

        int cellsToCheck = Mathf.CeilToInt(radius / Mathf.Min(gridSize.x, gridSize.y));

        for (int dx = -cellsToCheck; dx <= cellsToCheck; ++dx)
        {
            for (int dz = -cellsToCheck; dz <= cellsToCheck; ++dz)
            {
                Vector2 nearbyCell = cell + new Vector2(dx, dz);
                if (cells.TryGetValue(nearbyCell, out var entitiesInCell))
                {
                    foreach (var otherEntity in entitiesInCell)
                    {
                        if (otherEntity == entity) continue;

                        float distance = Vector2.Distance(
                            new Vector2(entity.transform.position.x, entity.transform.position.z),
                            new Vector2(otherEntity.transform.position.x, otherEntity.transform.position.z));

                        if (distance <= radius)
                        {
                            nearbyEntities.Add(otherEntity);
                        }
                    }
                }
            }
        }

        return nearbyEntities;
    }



    // Convert 3D position to 2D cell
    public Vector2 GetCellForPosition(Vector3 position)
    {
        return new Vector2(Mathf.Floor(position.x / gridSize.x), Mathf.Floor(position.z / gridSize.y));
    }
}
