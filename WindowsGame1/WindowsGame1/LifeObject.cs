using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Audio;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.GamerServices;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using Microsoft.Xna.Framework.Media;

namespace WindowsGame1
{
     public enum LifeObjectBehavior
     {
         Sun,
         Cloud,
         Air,
         Grass
     }

     public interface IDrawableUpdatable
     {
          int Depth { get; set; } 
          void Draw(SpriteBatchEx spriteBatch, GameTime time);
          void Update(Game1 game, GameTime time);

 
     }
   public class LifeObject:IDrawableUpdatable
    {
        public Texture2D Texture { get; set; }
        public Texture2D TextureGrayscale;
        public Vector2 Position { get; set; }
        public Vector2 TargetPosition; // Позиция частицы
        public Vector2 Velocity { get; set; }        // Скорость частицы
        public float Angle { get; set; }            // Угол поворота частицы
        public float AngularVelocity { get; set; }    // Угловая скорость частицы
        public Vector4 targetColor;
        public Vector4 color;// Цвет частицы
        public float Size { get; set; }
        public float Size2 = 1;// Размер частицы
        public float Size2realtime = 0;
        //float sizeVelocity = 0;
        public float alpha = 1f;
        private Vector2 origin;
        public float range;
        public MusicSrc childMusicSrc;
        public bool active = false;
        LifeObjectBehavior Behavior;
        public int Depth { get; set; }
        IDrawableUpdatable child;
        


        public LifeObject(Texture2D texture, Vector2 position, float size, Game1 game, LifeObjectBehavior behavior, int depth)
        {

            Texture = texture;
            Position = position;
            TargetPosition = position;
            Velocity = new Vector2(0);
            Angle = 0;
            AngularVelocity = 0;
            Size = size;
            Behavior = behavior;
            Depth = depth;
            
            color = GetColorFromTexture(texture);
            color.W = alpha;
            TextureGrayscale = MakeGrayscale(texture, game);
            origin = new Vector2(Texture.Width / 2, Texture.Height / 2);
            range = Texture.Width / 2 * Size * Size2realtime;

           

            if (Behavior == LifeObjectBehavior.Air)
            {
                color = Color.DeepSkyBlue.ToVector4();
            }
            if (Behavior == LifeObjectBehavior.Grass)
            {
                color = Color.ForestGreen.ToVector4();
            }

            childMusicSrc = new MusicSrc(game.textures["player1"], position, new Vector2(0), 0f, 0f, 0, 0, 0.4f, 0.5f, game, color);
            childMusicSrc.parentLifeObj.Add(this);
            game.musics.Add(childMusicSrc);
        }

        public void Update(Game1 game, GameTime time)
        {
            if (active)
            {
                if (Behavior == LifeObjectBehavior.Grass)
                {
                    if (child == null)
                    {
                        GrassField grass = new GrassField(new Rectangle(0, (int)(game.graphics.PreferredBackBufferHeight * 0.85), game.graphics.PreferredBackBufferWidth, (int)(game.graphics.PreferredBackBufferHeight * 0.25)), 256);
                        grass.Game = game;
                        grass.Depth = Depth;
                        child = grass;
                        game.AddIDrawableUpdatable(child);
                    }
                }

            }
            else
            {
                if (child != null)
                {
                    game.RemoveIDrawableUpdatable(child);
                    child = null;
                }
 
            }
        }

        Vector4 GetColorFromTexture(Texture2D textur)
        {
            Vector4 result=new Vector4(0);
            Color[] retrievedColor = new Color[1];
            Rectangle sourceRectangle = new Rectangle(0, 0, 1, 1);
            textur.GetData<Color>(0,sourceRectangle,retrievedColor, 0, 1);
            result = retrievedColor[0].ToVector4();
            return result;
        }

        Texture2D MakeGrayscale(Texture2D textur,Game1 game)
        {
            Texture2D result = new Texture2D(game.spriteBatch.GraphicsDevice, textur.Width, textur.Height);
            Color[] bitmap = new Color[textur.Width * textur.Height];

            textur.GetData(bitmap);

            for (int i = 0; i < textur.Width * textur.Height; i++)
            {
                //byte grayscale = (byte)(bitmap[i].R * 0.3f +
                //       bitmap[i].G * 0.59f + bitmap[i].B * 0.11f);
                //bitmap[i].R = grayscale;
                //bitmap[i].G = grayscale;
                //bitmap[i].B = grayscale;
                if (bitmap[i]!=Color.Black)
                {
                    bitmap[i] = Color.Transparent;
                    
                   
                }
            }

            result.SetData(bitmap);
            return result;
        }

        public void Draw(SpriteBatchEx spriteBatch, GameTime time) // Прорисовка частички
        {

            if (Behavior == LifeObjectBehavior.Air)
            {
                if (active)
                    spriteBatch.DrawRectangle(new Vector2(0, 0), new Vector2(800, 408), new Color(color));
 
            }
            else if (Behavior == LifeObjectBehavior.Grass)
            {
                //if (active)
                  //  spriteBatch.DrawRectangle(new Vector2(0, 250), new Vector2(800, 480), new Color(color));

            }
            else
            {
                if (active)
                    spriteBatch.Draw(Texture, Position, null, Color.White, Angle, origin, Size, SpriteEffects.None, 0f);
                else
                    spriteBatch.Draw(TextureGrayscale, Position, null, Color.White, Angle, origin, Size, SpriteEffects.None, 0f);
            }
            //if (childMusicSrc != null)
            //  spriteBatch.DrawLine(childMusicSrc.Position, Position, Color.Black, 1);
        }

    }
}
